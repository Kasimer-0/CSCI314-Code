# Entities/donee_action.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import bcrypt
import jwt

from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserAccount, Activity, Bookmark, Donation

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class DonationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Donation amount must be strictly positive")
    message: Optional[str] = None
    anonymous: bool = False

class DoneeLoginRequest(BaseModel):
    email: EmailStr
    password: str

class DoneeToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class DoneeEntity:

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False

    @staticmethod
    def login_donee(db: Session, login_data: DoneeLoginRequest):
        account = db.query(UserAccount).filter(UserAccount.email == login_data.email).first()

        if not account or not DoneeEntity.verify_password(login_data.password, account.password_hash):
            return None, "Incorrect email or password."
        
        if not account.profile or account.profile.role_id != 1:
            return None, "Access denied. Only Donees can log in here."
            
        if account.status == "Suspended" or account.is_suspended:
            return None, "This account has been suspended."

        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = jwt.encode({"sub": account.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"access_token": token, "token_type": "bearer"}, None

    @staticmethod
    def search_activities(db: Session, title: Optional[str]):
        query = db.query(Activity).filter(Activity.status == "Ongoing")
        if title:
            query = query.filter(Activity.title.ilike(f"%{title}%"))
        return query.all(), None

    @staticmethod
    def view_activity(db: Session, activity_id: int):
        activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
        if not activity:
            return None, "Activity not found."
        
        # Update view count
        activity.view_count += 1
        db.commit()
        db.refresh(activity)
        
        return activity, None

    @staticmethod
    def toggle_favorite(db: Session, activity_id: int, profile_id: int):
        existing = db.query(Bookmark).filter(Bookmark.user_id == profile_id, Bookmark.activity_id == activity_id).first()
        
        if existing:
            db.delete(existing)
            db.commit()
            return {"message": "Activity removed from favorites", "is_bookmarked": False}, None
        else:
            new_bookmark = Bookmark(user_id=profile_id, activity_id=activity_id)
            db.add(new_bookmark)
            db.commit()
            return {"message": "Activity saved to favorites", "is_bookmarked": True}, None

    @staticmethod
    def get_favorites(db: Session, profile_id: int, title_query: Optional[str] = None):
        query = db.query(Bookmark).filter(Bookmark.user_id == profile_id)
        favorites = query.all()
        
        if title_query:
            favorites = [fav for fav in favorites if fav.activity and title_query.lower() in fav.activity.title.lower()]
        return favorites, None

    @staticmethod
    def make_donation(db: Session, activity_id: int, profile_id: int, donation_data: DonationRequest):
        activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
        if not activity:
            return None, "Activity not found."
            
        if activity.status != "Ongoing":
            return None, "This activity is closed and no longer accepts donations."
            
        activity.current_amount += donation_data.amount
        
        new_donation = Donation(
            activity_id=activity_id,
            user_id=profile_id,
            amount=donation_data.amount,
            message=donation_data.message,
            is_anonymous=donation_data.anonymous
        )
        
        db.add(new_donation)
        db.commit()
        db.refresh(new_donation)
        
        return {"message": "Donation successful", "new_amount": activity.current_amount, "donation_id": new_donation.donation_id}, None

    @staticmethod
    def search_past_donations(db: Session, profile_id: int):
        donations = db.query(Donation).filter(Donation.user_id == profile_id).order_by(Donation.created_at.desc()).all()
        return donations, None

    @staticmethod
    def view_past_donation_detail(db: Session, donation_id: int, profile_id: int):
        donation = db.query(Donation).filter(Donation.donation_id == donation_id, Donation.user_id == profile_id).first()
        if not donation:
            return None, "Donation record not found."
        return donation, None