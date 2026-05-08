from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Activity, Donation
from dependencies import get_db

class PlatformReportEntity:
    @staticmethod
    def generate_stats(start_date: datetime, end_date: datetime):
        """Entity Logic (Story 40, 41, 42)"""
        db: Session = next(get_db())
        try:
            new_activities = db.query(func.count(Activity.activity_id)).filter(
                Activity.created_at >= start_date, Activity.created_at <= end_date
            ).scalar() or 0
            
            donations = db.query(func.count(Donation.donation_id), func.sum(Donation.amount)).filter(
                Donation.created_at >= start_date, Donation.created_at <= end_date
            ).first()
            
            return {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "new_activities_launched": new_activities,
                "total_donations_amount": donations[1] or 0.0,
                "transactions_count": donations[0] or 0
            }, None
        finally:
            db.close()