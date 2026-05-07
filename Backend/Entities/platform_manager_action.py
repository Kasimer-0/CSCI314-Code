# Entities/platform_manager_action.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt
import jwt

from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_db
from models import UserAccount, Category, Activity, Donation

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class PlatformManagerLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PlatformManagerToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class PlatformManagerEntity:

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False

    @staticmethod
    def login_manager(login_data: PlatformManagerLoginRequest):
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.email == login_data.email).first()

            if not account or not PlatformManagerEntity.verify_password(login_data.password, account.password_hash):
                return None, "Incorrect email or password."
            
            if not account.profile or account.profile.role_id != 3:
                return None, "Access denied. Only Platform Managers can log in here."
                
            if account.status == "Suspended" or account.is_suspended:
                return None, "This account has been suspended."

            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = jwt.encode({"sub": account.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
            
            return {"access_token": token, "token_type": "bearer"}, None
        finally:
            db.close()

    @staticmethod
    def create_category(cat_data: CategoryCreate):
        db: Session = next(get_db())
        try:
            new_cat = Category(
                name=cat_data.name,
                description=cat_data.description,
                is_archived=False
            )
            db.add(new_cat)
            db.commit()
            db.refresh(new_cat)
            return new_cat, None
        finally:
            db.close()

    @staticmethod
    def view_category(category_id: int):
        db: Session = next(get_db())
        try:
            category = db.query(Category).filter(Category.category_id == category_id).first()
            if not category:
                return None, "Category not found."
            return category, None
        finally:
            db.close()

    @staticmethod
    def update_category(category_id: int, cat_data: CategoryUpdate):
        db: Session = next(get_db())
        try:
            category = db.query(Category).filter(Category.category_id == category_id).first()
            if not category:
                return None, "Category not found."
                
            if cat_data.name is not None:
                category.name = cat_data.name
            if cat_data.description is not None:
                category.description = cat_data.description
                
            db.commit()
            db.refresh(category)
            return category, None
        finally:
            db.close()

    @staticmethod
    def suspend_category(category_id: int):
        db: Session = next(get_db())
        try:
            category = db.query(Category).filter(Category.category_id == category_id).first()
            if not category:
                return None, "Failed to suspend category."
                
            category.is_archived = True
            db.commit()
            return {"message": f"Category {category_id} suspended successfully."}, None
        finally:
            db.close()

    @staticmethod
    def search_categories(name_query: Optional[str]):
        db: Session = next(get_db())
        try:
            query = db.query(Category)
            if name_query:
                query = query.filter(Category.name.ilike(f"%{name_query}%"))
            return query.all(), None
        finally:
            db.close()

    @staticmethod
    def generate_stats_by_date(start_date: datetime, end_date: datetime):
        db: Session = next(get_db())
        try:
            new_activities_count = db.query(func.count(Activity.activity_id)).filter(
                Activity.created_at >= start_date, Activity.created_at <= end_date
            ).scalar() or 0
            
            donations_stats = db.query(
                func.count(Donation.donation_id), 
                func.sum(Donation.amount)
            ).filter(
                Donation.created_at >= start_date, Donation.created_at <= end_date
            ).first()
            
            transactions_count = donations_stats[0] or 0
            total_amount = donations_stats[1] or 0.0
            
            return {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "new_activities_launched": new_activities_count,
                "total_donations_amount": total_amount,
                "transactions_count": transactions_count
            }, None
        finally:
            db.close()