from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Activity, Donation
from dependencies import get_db

class PlatformReportEntity:
    @staticmethod
    def generate_stats(start_date: datetime, end_date: datetime):
        """[Story 40, 41, 42] Core statistical logic: Generate platform operation data reports.
            This method is responsible for aggregating data across tables and calculating the following within a specified time range:
            1. Number of newly initiated fundraising campaigns (Activity table)
            2. Total donation amount (Donation table)
            3. Number of successful transactions (Donation table)"""
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