from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Session, relationship
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional
from database import Base, get_db

# ==========================================
# 1. Pydantic Models
# ==========================================
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
# 2. BCE Entity: Activity
# ==========================================
class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    fundraiser_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False) 
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(String)
    target_amount = Column(Float, nullable=False) 
    current_amount = Column(Float, default=0.0)
    status = Column(String, default="Pending")
    is_private = Column(Boolean, default=False) 
    view_count = Column(Integer, default=0)    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # The relationship name here must match the one in UserProfile.
    creator = relationship("UserProfile", back_populates="activities") 
    bookmarks = relationship("Bookmark", back_populates="activity")
    donations = relationship("Donation", back_populates="activity")
    category = relationship("Category", back_populates="activities")

    # --- Behavior: Business logic ---
    @classmethod
    def create_activity(cls, activity_data: ActivityCreate, profile_id: int):
        """Entity Logic (Story 13): Create Activity"""
        db: Session = next(get_db())
        try:
            # Note: The fundraiser_id here must match the field name above!
            new_activity = cls(
                fundraiser_id=profile_id, 
                title=activity_data.title,
                description=activity_data.description,
                category_id=activity_data.category_id,
                target_amount=activity_data.target_amount,
                is_private=activity_data.is_private
            )
            db.add(new_activity)
            db.commit()
            db.refresh(new_activity)
            return new_activity, None
        except Exception as e:
            return None, str(e)
        finally:
            db.close()

    @classmethod
    def get_activity(cls, activity_id: int, profile_id: int):
        """Entity Logic (Story 14 & 23): View activity details"""
        db: Session = next(get_db())
        try:
            activity = db.query(cls).filter(cls.activity_id == activity_id, cls.fundraiser_id == profile_id).first()
            if not activity: 
                return None, "Activity not found or unauthorized."
            return activity, None
        finally:
            db.close()

    @classmethod
    def update_activity(cls, activity_id: int, title: str, profile_id: int):
        """Entity Logic (Story 15): Update activity title"""
        db: Session = next(get_db())
        try:
            activity = db.query(cls).filter(cls.activity_id == activity_id, cls.fundraiser_id == profile_id).first()
            if not activity: 
                return None, "Activity not found or unauthorized."
            
            activity.title = title
            db.commit()
            db.refresh(activity)
            return activity, None
        finally:
            db.close()

    @classmethod
    def suspend_activity(cls, activity_id: int, profile_id: int):
        """Entity Logic (Story 16): Suspend activity"""
        db: Session = next(get_db())
        try:
            activity = db.query(cls).filter(cls.activity_id == activity_id, cls.fundraiser_id == profile_id).first()
            if not activity: 
                return None, "Activity not found or unauthorized."
            
            activity.status = "Suspended"
            db.commit()
            db.refresh(activity)
            return activity, None
        finally:
            db.close()

    @classmethod
    def search_activities(cls, title: Optional[str], profile_id: int):
        """Entity Logic (Story 17): Search for ongoing/pending activities"""
        db: Session = next(get_db())
        try:
            # Only search for activities under this Fundraiser that are in the Ongoing or Pending status.
            query = db.query(cls).filter(
                cls.fundraiser_id == profile_id, 
                cls.status.in_(["Pending", "Ongoing"])
            )
            if title:
                query = query.filter(cls.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()        

    @classmethod
    def get_activity_views(cls, activity_id: int, profile_id: int):
        """Entity Logic (Story 20): Track Views"""
        db: Session = next(get_db())
        try:
            activity = db.query(cls).filter(cls.activity_id == activity_id, cls.fundraiser_id == profile_id).first()
            if not activity: return None, "Activity not found or unauthorized."
            return {"activity_id": activity.activity_id, "title": activity.title, "views": activity.view_count}, None
        finally:
            db.close()

    @classmethod
    def get_activity_shortlists(cls, activity_id: int, profile_id: int):
        """Entity Logic (Story 21): Track Shortlists"""
        db: Session = next(get_db())
        try:
            # Importing here to avoid circular imports, as Bookmark also imports Activity.
            from Entities.donee_favorite import Bookmark

            activity = db.query(cls).filter(cls.activity_id == activity_id, cls.fundraiser_id == profile_id).first()
            if not activity: return None, "Activity not found or unauthorized."

            bookmark_count = db.query(Bookmark).filter(Bookmark.activity_id == activity_id).count()
            return {"activity_id": activity.activity_id, "title": activity.title, "shortlisted_times": bookmark_count}, None
        finally:
            db.close()

    @classmethod
    def search_history(cls, title: Optional[str], profile_id: int):
        """Entity Logic (Story 22): Search History"""
        db: Session = next(get_db())
        try:
            query = db.query(cls).filter(cls.fundraiser_id == profile_id, cls.status.in_(["Closed", "Suspended"]))
            if title:
                query = query.filter(cls.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()