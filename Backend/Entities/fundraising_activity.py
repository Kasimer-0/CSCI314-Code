# Entities/fundraising_activity.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import bcrypt
import jwt

from models import Activity, UserAccount, Bookmark
from dependencies import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class FundraiserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class FundraiserToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ActivityCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    category_id: int = Field(..., gt=0)
    target_amount: float = Field(..., gt=10)
    is_private: bool = False

class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20)
    target_amount: Optional[float] = Field(None, gt=10)
    is_private: Optional[bool] = None

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class FundraisingActivityEntity:
    
    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False

    @staticmethod
    def login_fundraiser(login_data: FundraiserLoginRequest):
        """Entity Logic (Story 18): Fundraiser Login"""
        db: Session = next(get_db())
        try:
            account = db.query(UserAccount).filter(UserAccount.email == login_data.email).first()
            if not account or not FundraisingActivityEntity.verify_password(login_data.password, account.password_hash):
                return None, "Incorrect email or password."

            # Ensure that only Fundraiser (role_id = 2) can log in.
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
    def create_activity(activity_data: ActivityCreate, profile_id: int):
        """Entity Logic (Story 13): Create Activity"""
        db: Session = next(get_db())
        try:
            new_activity = Activity(
                fundraiser_id=profile_id,
                category_id=activity_data.category_id,
                title=activity_data.title,
                description=activity_data.description,
                target_amount=activity_data.target_amount,
                is_private=activity_data.is_private,
                status="Ongoing"
            )
            db.add(new_activity)
            db.commit()
            db.refresh(new_activity)
            return new_activity, None
        finally:
            db.close()

    @staticmethod
    def get_activity(activity_id: int, profile_id: int):
        """Entity Logic (Story 14 & 23): View Activity"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
            if not activity:
                return None, "Activity not found or unauthorized."
            return activity, None
        finally:
            db.close()

    @staticmethod
    def update_activity(activity_id: int, title: str, profile_id: int):
        """Entity Logic (Story 15): Update Activity"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
            if not activity:
                return None, "Failed to update activity."
                
            activity.title = title
            db.commit()
            db.refresh(activity)
            return activity, None
        finally:
            db.close()

    @staticmethod
    def suspend_activity(activity_id: int, profile_id: int):
        """Entity Logic (Story 16): Suspend Activity"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
            if not activity:
                return None, "Failed to suspend activity."
                
            activity.status = "Suspended"
            db.commit()
            db.refresh(activity)
            return activity, None
        finally:
            db.close()

    @staticmethod
    def search_activities(title: Optional[str], profile_id: int):
        """Entity Logic (Story 17): Search Ongoing Activities"""
        db: Session = next(get_db())
        try:
            query = db.query(Activity).filter(Activity.fundraiser_id == profile_id, Activity.status == "Ongoing")
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()

    @staticmethod
    def get_activity_stats(activity_id: int, profile_id: int):
        """Entity Logic (Story 20): Track potential interests (views and shortlisted times)"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
            if not activity:
                return None, "Activity not found or unauthorized."
            
            # Calculate the number of times this activity has been added to bookmarks (shortlisted)
            bookmark_count = db.query(Bookmark).filter(Bookmark.activity_id == activity_id).count()
            
            return {
                "activity_id": activity.activity_id,
                "title": activity.title,
                "views": activity.view_count,
                "shortlisted_times": bookmark_count
            }, None
        finally:
            db.close()

    @staticmethod
    def search_history(title: Optional[str], profile_id: int):
        """Entity Logic (Story 22): Search History (Closed Activities)"""
        db: Session = next(get_db())
        try:
            query = db.query(Activity).filter(Activity.fundraiser_id == profile_id, Activity.status == "Closed")
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()