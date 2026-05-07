# Entities/user_account.py

from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy.orm import Session
import bcrypt
from models import UserAccount 
from dependencies import get_db
import jwt
from datetime import timedelta
from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class UserAccountCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class UserAccountEntity:
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False
        
    @staticmethod
    def login_admin(login_data):
        """Entity Logic (Story 11): Login admin and issue JWT"""
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.email == login_data.email).first()       
            if not account or not UserAccountEntity.verify_password(login_data.password, account.password_hash):
                return None, "Incorrect email or password."
            if account.status == "Suspended" or account.is_suspended:
                return None, "Your account has been suspended."
            if not account.profile or account.profile.role_id != 0:
                return None, "Access Denied. Admin privileges required."
            
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode = {"sub": account.email, "exp": expire}
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            
            return {"access_token": encoded_jwt, "token_type": "bearer"}, None
        finally:
            db.close()

    @staticmethod
    def create_account(account_data: UserAccountCreate):
        """Entity Logic (Story 6): Insert new account into database"""
        db: Session = next(get_db())
        try:
            existing = db.query(UserAccount).filter(UserAccount.email == account_data.email).first()
            if existing:
                return None, "Email already registered in the system."

            hashed_password = UserAccountEntity.get_password_hash(account_data.password)

            new_account = UserAccount(
                email=account_data.email,
                password_hash=hashed_password,
                status="Pending",
                is_suspended=False,
                created_at=datetime.now(timezone.utc)
            )

            db.add(new_account)
            db.commit()
            db.refresh(new_account)
            return {"user_id": new_account.account_id, "email": new_account.email, "status": new_account.status}, None
        finally:
            db.close()

    @staticmethod
    def get_account(account_id: int):
        """Entity Logic (Story 7): Get single user account safely"""
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.account_id == account_id).first()
            if not account:
                return None, "User account not found."
                          
            return {
                "account_id": account.account_id,
                "email": account.email,
                "status": account.status,
                "is_suspended": account.is_suspended
            }, None
        finally:
            db.close()
    @staticmethod
    def update_account(account_id: int, new_email: str):
        """Entity Logic (Story 8): Update user email"""
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.account_id == account_id).first()
            if not account:
                return None, "User account not found."
                
            account.email = new_email
            db.commit()
            db.refresh(account)
            return account, None
        finally:
            db.close()

    @staticmethod
    def suspend_account(account_id: int):
        """Entity Logic (Story 9): Suspend user account"""
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.account_id == account_id).first()
            if not account:
                return None, "User account not found."
                
            account.status = "Suspended"
            account.is_suspended = True
            db.commit()
            db.refresh(account)
            return account, None
        finally:
            db.close()

    @staticmethod
    def search_accounts(email_query: Optional[str]):
        """Entity Logic (Story 10): Search user accounts"""
        db: Session = next(get_db())
        try:
            query = db.query(UserAccount)
            if email_query:
                query = query.filter(UserAccount.email.ilike(f"%{email_query}%"))
            return query.all(), None
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_email_for_auth(email: str):
        """Entity Logic: Helper for Token validation in dependencies"""
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.email == email).first()
            return account
        finally:
            db.close()
