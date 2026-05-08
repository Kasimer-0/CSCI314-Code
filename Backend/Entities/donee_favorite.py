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
            return query.all(), None
        finally:
            db.close()