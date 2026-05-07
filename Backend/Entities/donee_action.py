# Entities/donee_action.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import bcrypt
import jwt

from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_db
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
    def login_donee(login_data: DoneeLoginRequest):
        """Entity Logic (Story 29)"""
        db: Session = next(get_db())
        try:
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
        finally:
            db.close()

    @staticmethod
    def search_activities(title: Optional[str]):
        """Entity Logic (Story 24)"""
        db: Session = next(get_db())
        try:
            query = db.query(Activity).filter(Activity.status == "Ongoing")
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()

    @staticmethod
    def view_activity(activity_id: int):
        """Entity Logic (Story 25)"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
            if not activity:
                return None, "Activity not found."
            
            # Update view count
            activity.view_count += 1
            db.commit()
            db.refresh(activity)
            
            return activity, None
        finally:
            db.close()

    @staticmethod
    def toggle_favorite(activity_id: int, profile_id: int):
        """Entity Logic (Story 26)"""
        db: Session = next(get_db())
        try:
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
        finally:
            db.close()

    @staticmethod
    def get_favorites(profile_id: int, title_query: Optional[str] = None):
        """Entity Logic (Story 27 & 28)"""
        db: Session = next(get_db())
        try:
            query = db.query(Bookmark).filter(Bookmark.user_id == profile_id)
            favorites = query.all()
            
            if title_query:
                favorites = [fav for fav in favorites if fav.activity and title_query.lower() in fav.activity.title.lower()]
            return favorites, None
        finally:
            db.close()

    @staticmethod
    def manage_favorites(profile_id: int, title: Optional[str] = None):
        """Entity Logic (Story 27 & 28): Get detailed bookmark data for card rendering"""
        db: Session = next(get_db())
        try:
            query = db.query(Bookmark).filter(Bookmark.user_id == profile_id)
            bookmarks = query.all()
            
            result = []
            for b in bookmarks:
                if not b.activity:
                    continue
                act = b.activity
                activity_title = act.title
                
                if title and title.lower() not in activity_title.lower():
                    continue
                    
                result.append({
                    "bookmark_id": b.bookmark_id,
                    "activity_id": b.activity_id,
                    "activity_title": activity_title,
                    "description": act.description,
                    "target_amount": act.target_amount,
                    "current_amount": act.current_amount,
                    "status": act.status
                })
            return result, None
        finally:
            db.close()

    @staticmethod
    def make_donation(activity_id: int, profile_id: int, donation_data: DonationRequest):
        """Helper Entity Logic for Donations"""
        db: Session = next(get_db())
        try:
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
        finally:
            db.close()

    @staticmethod
    def search_past_donations(profile_id: int, title: Optional[str] = None):
        """Entity Logic (Story 31): Search donations safely"""
        db: Session = next(get_db())
        try:
            donations = db.query(Donation).filter(Donation.user_id == profile_id).order_by(Donation.created_at.desc()).all()
            result = []
            for d in donations:
                activity_title = d.activity.title if d.activity else "Unknown Activity"
                
                if title and title.lower() not in activity_title.lower():
                    continue
                    
                result.append({
                    "donation_id": d.donation_id,
                    "amount": d.amount,
                    "created_at": d.created_at.isoformat(),
                    "activity_title": activity_title
                })
            return result, None
        finally:
            db.close()

    @staticmethod
    def view_past_donation_detail(donation_id: int, profile_id: int):
        """Entity Logic (Story 32): Get safe dictionary for specific donation"""
        db: Session = next(get_db())
        try:
            donation = db.query(Donation).filter(
                Donation.donation_id == donation_id, 
                Donation.user_id == profile_id
            ).first()
            
            if not donation:
                return None, "Donation record not found."
            
            # 在 db.close() 之前手动组装所有字段
            return {
                "donation_id": donation.donation_id,
                "amount": donation.amount,
                "message": donation.message or "No message left.",
                "is_anonymous": donation.is_anonymous,
                "created_at": donation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "activity_title": donation.activity.title if donation.activity else "Unknown Activity"
            }, None
        finally:
            db.close()
