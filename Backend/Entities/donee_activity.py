from typing import Optional
from sqlalchemy.orm import Session
from models import Activity
from dependencies import get_db

class DoneeActivityEntity:
    @staticmethod
    def search_activities(title: Optional[str]):
        """Entity Logic (Story 24): Search activities"""
        db: Session = next(get_db())
        try:
            query = db.query(Activity).filter(Activity.status == "Ongoing", Activity.is_private == False)
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            return query.all(), None
        finally:
            db.close()

    @staticmethod
    def get_activity(activity_id: int):
        """Entity Logic (Story 25): View activity details"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.status == "Ongoing").first()
            if not activity:
                return None, "Activity not found or no longer active."
            # Increase page views
            activity.view_count += 1
            db.commit()
            db.refresh(activity)
            return activity, None
        finally:
            db.close()