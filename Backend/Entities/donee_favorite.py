from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Session, relationship
from datetime import datetime, timezone
from typing import Optional
from database import Base, get_db

# ==========================================
# BCE Entity: Bookmark
# ==========================================
class Bookmark(Base):
    __tablename__ = "bookmarks"

    # --- State: Database table field ---
    bookmark_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.activity_id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user_profile = relationship("UserProfile", back_populates="bookmarks")
    activity = relationship("Activity", back_populates="bookmarks")

    # --- Behavior: Business logic methods ---
    @classmethod
    def toggle_favorite(cls, activity_id: int, profile_id: int):
        """Entity Logic (Story 26): Save to favorites"""
        db: Session = next(get_db())
        try:
            existing = db.query(cls).filter(cls.activity_id == activity_id, cls.user_id == profile_id).first()
            if existing:
                db.delete(existing)
                db.commit()
                return {"message": "Removed from favorites."}, None
            else:
                new_fav = cls(activity_id=activity_id, user_id=profile_id)
                db.add(new_fav)
                db.commit()
                return {"message": "Added to favorites!"}, None
        finally:
            db.close()

    @classmethod
    def get_favorites(cls, profile_id: int, title: Optional[str]):
        """Entity Logic (Story 27 & 28): Manage favorites"""
        db: Session = next(get_db())
        try:
            # Importing here to avoid circular imports, as Activity also imports Bookmark.
            from Entities.fundraising_activity import Activity

            query = db.query(cls).join(Activity).filter(cls.user_id == profile_id)
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            bookmarks = query.all()
            
            result = []
            for bookmark in bookmarks:
                result.append({
                    "bookmark_id": bookmark.bookmark_id,
                    "activity": {
                        "activity_id": bookmark.activity.activity_id,
                        "title": bookmark.activity.title,
                        "description": bookmark.activity.description,
                        "target_amount": bookmark.activity.target_amount,
                        "current_amount": bookmark.activity.current_amount,
                        "status": bookmark.activity.status,
                        "view_count": bookmark.activity.view_count,
                        "is_private": bookmark.activity.is_private,
                        "created_at": bookmark.activity.created_at.isoformat() if bookmark.activity.created_at else None
                    }
                })
            return result, None
        finally:
            db.close()