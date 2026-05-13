from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Session, relationship
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional
from database import Base, get_db

from Entities.fundraising_activity import Activity

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class DonationRequest(BaseModel):
    amount: float = Field(..., gt=0)
    message: Optional[str] = None
    anonymous: bool = False

# ==========================================
# 2. BCE Entity: Donation
# ==========================================
class Donation(Base):
    __tablename__ = "donations"

    # --- State: Database table field ---
    donation_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.activity_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    amount = Column(Float, nullable=False)
    message = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    donee_profile = relationship("UserProfile", back_populates="donations")
    activity = relationship("Activity", back_populates="donations")

    # --- Behavior: Business logic methods ---
    @classmethod
    def donate_to_activity(cls, activity_id: int, profile_id: int, donation_data: DonationRequest):
        """Entity Logic: Make a donation"""
        db: Session = next(get_db())
        try:
            # Importing here to avoid circular imports, as Activity also imports Donation.
            from Entities.fundraising_activity import Activity

            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.status == "Ongoing").first()
            if not activity: return None, "Activity not available for donation."
            
            new_donation = cls(
                activity_id=activity_id,
                user_id=profile_id,
                amount=donation_data.amount,
                message=donation_data.message,
                is_anonymous=donation_data.anonymous
            )
            db.add(new_donation)
            
            # Synchronize and update the total amount raised in the Activity
            activity.current_amount += donation_data.amount
            db.commit()
            return {"message": "Donation successful!"}, None
        finally:
            db.close()

    @classmethod
    def search_past_donations(cls, profile_id: int, title: Optional[str]):
        """Entity Logic (Story 31): Search past donations"""
        db: Session = next(get_db())
        try:
            donations = db.query(cls).filter(cls.user_id == profile_id).order_by(cls.created_at.desc()).all()
            result = []
            for d in donations:
                activity_title = d.activity.title if d.activity else "Unknown Activity"
                if title and title.lower() not in activity_title.lower(): continue
                result.append({
                    "donation_id": d.donation_id,
                    "amount": d.amount,
                    "created_at": d.created_at.isoformat(),
                    "activity_title": activity_title
                })
            return result, None
        finally:
            db.close()

    @classmethod
    def view_past_donation_detail(cls, donation_id: int, profile_id: int):
        """Entity Logic (Story 32): View past donation"""
        db: Session = next(get_db())
        try:
            donation = db.query(cls).filter(cls.donation_id == donation_id, cls.user_id == profile_id).first()
            if not donation: return None, "Donation record not found."
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