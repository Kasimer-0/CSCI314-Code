# [Replaced] Entities/user_profile.py

from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from models import UserProfile, UserAccount

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class UserProfileCreate(BaseModel):
    account_id: int
    username: str
    phone_number: Optional[str] = None
    role_id: int

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class UserProfileEntity:

    @staticmethod
    def create_profile(db: Session, profile_data: UserProfileCreate):
        """Entity Logic (Story 1): Link profile data to an existing account"""
        # 1. Check if Account exists
        account = db.query(UserAccount).filter(UserAccount.account_id == profile_data.account_id).first()
        if not account:
            return None, "User account not found. Please create an account first."
        
        # 2. Check if Profile already exists for this Account
        existing_profile = db.query(UserProfile).filter(UserProfile.account_id == profile_data.account_id).first()
        if existing_profile:
            return None, "Profile already exists for this account."

        # 3. Create Profile
        new_profile = UserProfile(
            account_id=profile_data.account_id,
            username=profile_data.username,
            phone_number=profile_data.phone_number,
            role_id=profile_data.role_id
        )
        db.add(new_profile)
        
        # 4. Refresh Activate Account status
        account.status = "Active"
        
        db.commit()
        db.refresh(new_profile)
        
        return new_profile, None

    @staticmethod
    def get_profile(db: Session, profile_id: int):
        """Entity Logic (Story 2): View user profile"""
        profile = db.query(UserProfile).filter(UserProfile.profile_id == profile_id).first()
        if not profile:
            return None, "User profile not found."
        return profile, None

    @staticmethod
    def update_profile(db: Session, profile_id: int, update_data: UserProfileUpdate):
        """Entity Logic (Story 3): Update user profile"""
        profile = db.query(UserProfile).filter(UserProfile.profile_id == profile_id).first()
        if not profile:
            return None, "User profile not found."

        if update_data.username is not None:
            profile.username = update_data.username
        if update_data.phone_number is not None:
            profile.phone_number = update_data.phone_number

        db.commit()
        db.refresh(profile)
        return profile, None

    @staticmethod
    def search_profiles(db: Session, username_query: Optional[str]):
        """Entity Logic (Story 5): Search user profiles"""
        query = db.query(UserProfile)
        if username_query:
            query = query.filter(UserProfile.username.ilike(f"%{username_query}%"))
        return query.all(), None