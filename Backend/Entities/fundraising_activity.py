from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from models import Activity, Bookmark
from dependencies import get_db

# ==========================================
# 1. Pydantic Models (Data Validation)
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
# 2. Entity Class (Business Logic & Database)
# ==========================================

class FundraisingActivityEntity:
    
    @staticmethod
    def create_activity(activity_data: ActivityCreate, profile_id: int):
        """Entity Logic (Story 13): Create Activity"""
        db: Session = next(get_db())
        try:
            new_activity = Activity(
                profile_id=profile_id,
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
        """Entity Logic (Story 15): Update Activity Title"""
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
    def get_activity_views(activity_id: int, profile_id: int):
        """Entity Logic (Story 20): Track the number of views"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
            if not activity:
                return None, "Activity not found or unauthorized."
            
            return {
                "activity_id": activity.activity_id,
                "title": activity.title,
                "views": activity.view_count
            }, None
        finally:
            db.close()

    @staticmethod
    def get_activity_shortlists(activity_id: int, profile_id: int):
        """Entity Logic (Story 21): Track the number of shortlists"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
            if not activity:
                return None, "Activity not found or unauthorized."
            
            # Count the number of times this activity was added to bookmarks
            bookmark_count = db.query(Bookmark).filter(Bookmark.activity_id == activity_id).count()
            
            return {
                "activity_id": activity.activity_id,
                "title": activity.title,
                "shortlisted_times": bookmark_count
            }, None
        finally:
            db.close()

    @staticmethod
    def search_history(title: Optional[str], profile_id: int):
        """Entity Logic (Story 22): Search History (Closed/Suspended Activities)"""
        db: Session = next(get_db())
        try:
            # History should include both Closed and Suspended activities
            query = db.query(Activity).filter(
                Activity.fundraiser_id == profile_id, 
                Activity.status.in_(["Closed", "Suspended"])
            )
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()