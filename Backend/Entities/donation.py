from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from models import Donation, Activity
from dependencies import get_db

class DonationRequest(BaseModel):
    amount: float = Field(..., gt=0)
    message: Optional[str] = None
    anonymous: bool = False

class DonationEntity:
    @staticmethod
    def donate_to_activity(activity_id: int, profile_id: int, donation_data: DonationRequest):
        """Entity Logic: Make a donation"""
        db: Session = next(get_db())
        try:
            activity = db.query(Activity).filter(Activity.activity_id == activity_id, Activity.status == "Ongoing").first()
            if not activity: return None, "Activity not available for donation."
            
            new_donation = Donation(
                activity_id=activity_id,
                user_id=profile_id,
                amount=donation_data.amount,
                message=donation_data.message,
                is_anonymous=donation_data.anonymous
            )
            db.add(new_donation)
            activity.current_amount += donation_data.amount
            db.commit()
            return {"message": "Donation successful!"}, None
        finally:
            db.close()

    @staticmethod
    def search_past_donations(profile_id: int, title: Optional[str]):
        """Entity Logic (Story 31): Search past donations"""
        db: Session = next(get_db())
        try:
            donations = db.query(Donation).filter(Donation.user_id == profile_id).order_by(Donation.created_at.desc()).all()
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

    @staticmethod
    def view_past_donation_detail(donation_id: int, profile_id: int):
        """Entity Logic (Story 32): View past donation"""
        db: Session = next(get_db())
        try:
            donation = db.query(Donation).filter(Donation.donation_id == donation_id, Donation.user_id == profile_id).first()
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