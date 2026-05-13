from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Session, relationship, joinedload
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import bcrypt
import jwt

from database import Base, get_db

SECRET_KEY = "CSIT314_2026_SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION_!@#$"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class UserAccountCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

# ==========================================
# 2. BCE Entity: UserAccount
# ==========================================
class UserAccount(Base):
    __tablename__ = "user_accounts"

    # --- State: Database table field ---
    account_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(String, default="Pending")
    is_suspended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship: One user account can have one profile
    profile = relationship("UserProfile", back_populates="account", uselist=False, cascade="all, delete-orphan")

    # --- Behavior: Business logic methods ---
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

    @classmethod
    def get_user_by_email_for_auth(cls, email: str):
        """Entity Logic: Helper for Token validation in dependencies"""
        db: Session = next(get_db())
        try:
            # Note: cls has been used instead of UserAccount and UserAccount
            account = db.query(cls).options(joinedload(cls.profile)).filter(cls.email == email).first()
            return account
        finally:
            db.close()
            
    @classmethod
    def create_account(cls, account_data: UserAccountCreate):
        """Entity Logic (Story 6): Insert new account into database"""
        db: Session = next(get_db())
        try:
            existing = db.query(cls).filter(cls.email == account_data.email).first()
            if existing:
                return None, "Email already registered in the system."

            hashed_password = cls.get_password_hash(account_data.password)

            new_account = cls(
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

    @classmethod
    def get_account(cls, account_id: int):
        """Entity Logic (Story 7): Get single user account safely"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).filter(cls.account_id == account_id).first()
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

    @classmethod
    def update_account(cls, account_id: int, new_email: str):
        """Entity Logic (Story 8): Update user email"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).filter(cls.account_id == account_id).first()
            if not account: return None, "User account not found."
                
            account.email = new_email
            db.commit()
            db.refresh(account)
            return account, None
        finally:
            db.close()

    @classmethod
    def suspend_account(cls, account_id: int):
        """Entity Logic (Story 9): Suspend user account"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).filter(cls.account_id == account_id).first()
            if not account: return None, "User account not found."
                
            account.status = "Suspended"
            account.is_suspended = True
            db.commit()
            db.refresh(account)
            return account, None
        finally:
            db.close()

    @classmethod
    def search_accounts(cls, email_query: Optional[str]):
        """Entity Logic (Story 10): Search user accounts"""
        db: Session = next(get_db())
        try:
            query = db.query(cls)
            if email_query:
                query = query.filter(cls.email.ilike(f"%{email_query}%"))
            return query.all(), None
        finally:
            db.close()

    @classmethod
    def login_admin(cls, login_data):
        """Entity Logic (Story 11): Login admin and issue JWT"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).options(joinedload(cls.profile)).filter(cls.email == login_data.email).first()       
            if not account or not cls.verify_password(login_data.password, account.password_hash):
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
    def logout_admin():
        """Entity Logic (Story 12): User administrator logout logic"""
        return {"message": "Logged out successfully from User Admin session."}, None

    @classmethod
    def login_fundraiser(cls, login_data):
        """Entity Logic (Story 18): Fundraiser Login"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).options(joinedload(cls.profile)).filter(cls.email == login_data.email).first()
            if not account or not cls.verify_password(login_data.password, account.password_hash):
                return None, "Incorrect email or password."
            if not account.profile or account.profile.role_id != 2:
                return None, "Access denied. Only Fundraisers can log in here."
            if account.status == "Suspended" or account.is_suspended:
                return None, "This account has been suspended."

            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = jwt.encode({"sub": account.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
            return {"access_token": token, "token_type": "bearer"}, None
        finally:
            db.close()

    @staticmethod
    def logout_fundraiser():
        """Entity Logic (Story 19): Fundraiser Logout"""
        return {"message": "Successfully logged out from Fundraiser session."}, None

    @classmethod
    def login_donee(cls, login_data):
        """Entity Logic (Story 29): Donee Login"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).options(joinedload(cls.profile)).filter(cls.email == login_data.email).first()
            if not account or not cls.verify_password(login_data.password, account.password_hash):
                return None, "Incorrect email or password."
            if not account.profile or account.profile.role_id != 1:
                return None, "Access denied. Only Donees can log in here."
            if account.status == "Suspended" or account.is_suspended:
                return None, "This account has been suspended."

            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = jwt.encode({"sub": account.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
            return {"access_token": token, "token_type": "bearer"}, None
        finally:
            db.close()

    @staticmethod
    def logout_donee():
        """Entity Logic (Story 30): Donee Logout"""
        return {"message": "Successfully logged out. Please discard your token."}, None
    
    @classmethod
    def login_manager(cls, login_data):
        """Entity Logic (Story 38): Platform Manager Login"""
        db: Session = next(get_db())
        try:
            account = db.query(cls).options(joinedload(cls.profile)).filter(cls.email == login_data.email).first()
            if not account or not cls.verify_password(login_data.password, account.password_hash):
                return None, "Incorrect email or password."
            if not account.profile or account.profile.role_id != 3:
                return None, "Access denied. Platform Manager privileges required."
            if account.status == "Suspended" or account.is_suspended:
                return None, "Your account has been suspended."

            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode = {"sub": account.email, "exp": expire}
            token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return {"access_token": token, "token_type": "bearer"}, None
        finally:
            db.close()

    @staticmethod
    def logout_manager():
        """Entity Logic (Story 39): Platform Manager Logout"""
        return {"message": "Successfully logged out from Platform Manager session."}, None