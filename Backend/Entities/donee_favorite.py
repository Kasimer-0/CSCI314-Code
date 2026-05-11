from typing import Optional
from sqlalchemy.orm import Session
from models import Bookmark, Activity
from dependencies import get_db

class FavoriteEntity:
    @staticmethod
    def toggle_favorite(activity_id: int, profile_id: int):
        """Entity Logic (Story 26): Save to favorites"""
        db: Session = next(get_db())
        try:
            existing = db.query(Bookmark).filter(Bookmark.activity_id == activity_id, Bookmark.user_id == profile_id).first()
            if existing:
                db.delete(existing)
                db.commit()
                return {"message": "Removed from favorites."}, None
            else:
                new_fav = Bookmark(activity_id=activity_id, user_id=profile_id)
                db.add(new_fav)
                db.commit()
                return {"message": "Added to favorites!"}, None
        finally:
            db.close()

    @staticmethod
    def get_favorites(profile_id: int, title: Optional[str]):
        """Entity Logic (Story 27 & 28): Manage favorites"""
        db: Session = next(get_db())
        try:
            query = db.query(Bookmark).join(Activity).filter(Bookmark.user_id == profile_id)
            if title:
                query = query.filter(Activity.title.ilike(f"%{title}%"))
            bookmarks = query.all()
            
            # Convert to dictionary format that matches front-end expectations
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