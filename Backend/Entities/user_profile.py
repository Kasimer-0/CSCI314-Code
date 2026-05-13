from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel
from typing import Optional

# 从基础配置导入
from database import Base, get_db

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class ProfileCreate(BaseModel):
    account_id: int
    profile_name: str
    profile_description: Optional[str] = None
    role_id: int

class ProfileUpdate(BaseModel):
    profile_description: str

# ==========================================
# 2. BCE Entity: UserProfile
# ==========================================
class UserProfile(Base):
    __tablename__ = "user_profiles"

    # --- State: Database table field ---
    profile_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("user_accounts.account_id"))
    profile_name = Column(String, index=True) 
    profile_description = Column(String, nullable=True)
    role_id = Column(Integer)
    status = Column(String, default="Active")
    is_suspended = Column(Boolean, default=False)

    # Establish a reverse association with Account
    account = relationship("UserAccount", back_populates="profile")

    activities = relationship("Activity", back_populates="creator")
    donations = relationship("Donation", back_populates="donee_profile")
    bookmarks = relationship("Bookmark", back_populates="user_profile")

    # --- Behavior: Business logic methods ---

    @classmethod
    def create_profile(cls, prof_data: ProfileCreate):
        """Entity Logic (Story 1): Create Profile"""
        db: Session = next(get_db())
        try:
            new_profile = cls(
                account_id=prof_data.account_id,
                profile_name=prof_data.profile_name,
                profile_description=prof_data.profile_description,
                role_id=prof_data.role_id
            )
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile, None
        except Exception as e:
            return None, str(e)
        finally:
            db.close()

    @classmethod
    def get_profile(cls, profile_id: int):
        """Entity Logic (Story 2): Get single user profile safely"""
        db: Session = next(get_db())
        try:
            profile = db.query(cls).filter(cls.profile_id == profile_id).first()
            if not profile:
                return None, "User profile not found."

            return {
                "profile_id": profile.profile_id,
                "account_id": profile.account_id,
                "profile_name": profile.profile_name,
                "profile_description": profile.profile_description,
                "role_id": profile.role_id,
                "status": profile.status
            }, None
        finally:
            db.close()

    @classmethod
    def update_profile(cls, profile_id: int, prof_data: ProfileUpdate):
        """Entity Logic (Story 3): Update Profile Description"""
        db: Session = next(get_db())
        try:
            profile = db.query(cls).filter(cls.profile_id == profile_id).first()
            if not profile:
                return None, "Profile not found."
            
            profile.profile_description = prof_data.profile_description
            db.commit()
            db.refresh(profile)
            return profile, None
        finally:
            db.close()

    @classmethod
    def suspend_profile(cls, profile_id: int):
        """Entity Logic (Story 4): Suspend user profile"""
        db: Session = next(get_db())
        try:
            profile = db.query(cls).filter(cls.profile_id == profile_id).first()
            if not profile:
                return None, "User profile not found."

            profile.status = "Suspended"
            profile.is_suspended = True
            
            db.commit()
            db.refresh(profile)
            return profile, None
        finally:
            db.close()

    @classmethod
    def search_profiles(cls, profile_name: Optional[str] = None):
        """Story 5: Search Profile (By profile_name)"""
        db: Session = next(get_db())
        try:
            query = db.query(cls)
            if profile_name:
                query = query.filter(cls.profile_name.ilike(f"%{profile_name}%"))
            return query.all(), None
        finally:
            db.close()