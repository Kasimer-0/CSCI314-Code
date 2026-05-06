# Entities/fundraising_activity.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from database import supabase

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
    def create_activity(activity_data: ActivityCreate, fundraiser_id: int):
        """Entity Logic: Insert new activity into database"""
        new_activity = {
            "fundraiser_id": fundraiser_id,
            "category_id": activity_data.category_id,
            "title": activity_data.title,
            "description": activity_data.description,
            "target_amount": activity_data.target_amount,
            "is_private": activity_data.is_private,
            "status": "Ongoing",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        res = supabase.table("activities").insert(new_activity).execute()
        if not res.data:
            return None, "Failed to create activity."
        return res.data[0], None

    @staticmethod
    def get_activity(activity_id: int, fundraiser_id: int):
        """Entity Logic: Retrieve a specific activity"""
        res = supabase.table("activities").select("*").eq("activity_id", activity_id).eq("fundraiser_id", fundraiser_id).execute()
        if not res.data:
            return None, "Activity not found or unauthorized."
        return res.data[0], None

    @staticmethod
    def update_activity(activity_id: int, title: str, fundraiser_id: int):
        """Entity Logic: Update activity title"""
        res = supabase.table("activities").update({"title": title}).eq("activity_id", activity_id).eq("fundraiser_id", fundraiser_id).execute()
        if not res.data:
            return None, "Failed to update activity."
        return res.data[0], None

    @staticmethod
    def suspend_activity(activity_id: int, fundraiser_id: int):
        """Entity Logic: Suspend/Archive an activity"""
        res = supabase.table("activities").update({"status": "Suspended"}).eq("activity_id", activity_id).eq("fundraiser_id", fundraiser_id).execute()
        if not res.data:
            return None, "Failed to suspend activity."
        return res.data[0], None

    @staticmethod
    def search_activities(title: Optional[str], fundraiser_id: int):
        """Entity Logic: Search ongoing activities"""
        query = supabase.table("activities").select("*").eq("fundraiser_id", fundraiser_id)
        if title:
            query = query.ilike("title", f"%{title}%")
        return query.execute().data, None

    @staticmethod
    def search_history(title: Optional[str], fundraiser_id: int):
        """Entity Logic: Search past (Closed) activities"""
        query = supabase.table("activities").select("*").eq("fundraiser_id", fundraiser_id).eq("status", "Closed")
        if title:
            query = query.ilike("title", f"%{title}%")
        return query.execute().data, None