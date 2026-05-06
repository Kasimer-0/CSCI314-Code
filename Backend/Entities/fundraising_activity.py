# Entities/fundraising_activity.py

from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from models import Activity

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
    def create_activity(db: Session, activity_data: ActivityCreate, profile_id: int):
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

    @staticmethod
    def get_activity(db: Session, activity_id: int, profile_id: int):
        activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
        if not activity:
            return None, "Activity not found or unauthorized."
        return activity, None

    @staticmethod
    def update_activity(db: Session, activity_id: int, title: str, profile_id: int):
        activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
        if not activity:
            return None, "Failed to update activity."
            
        activity.title = title
        db.commit()
        db.refresh(activity)
        return activity, None

    @staticmethod
    def suspend_activity(db: Session, activity_id: int, profile_id: int):
        activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.fundraiser_id == profile_id).first()
        if not activity:
            return None, "Failed to suspend activity."
            
        activity.status = "Suspended"
        db.commit()
        db.refresh(activity)
        return activity, None

    @staticmethod
    def search_activities(db: Session, title: Optional[str], profile_id: int):
        query = db.query(Activity).filter(Activity.fundraiser_id == profile_id)
        if title:
            query = query.filter(Activity.title.ilike(f"%{title}%"))
        return query.all(), None

    @staticmethod
    def search_history(db: Session, title: Optional[str], profile_id: int):
        query = db.query(Activity).filter(Activity.fundraiser_id == profile_id, Activity.status == "Closed")
        if title:
            query = query.filter(Activity.title.ilike(f"%{title}%"))
        return query.all(), None