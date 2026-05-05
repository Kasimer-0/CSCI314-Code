from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone

import schemas
from database import supabase
from dependencies import get_current_fundraiser 

# Create Router instances and automatically add prefixes and category tags.
router = APIRouter(
    prefix="/fundraiser/activities",
    tags=["Sprint 2 - Fundraiser Activities"]
)

@router.post("/", response_model=schemas.ActivityResponse)
def create_activity(activity: schemas.ActivityCreate, current_user: dict = Depends(get_current_fundraiser)):
    new_activity = {
        "fundraiser_id": current_user["user_id"],
        "category_id": activity.category_id,
        "title": activity.title,
        "description": activity.description,
        "target_amount": activity.target_amount,
        "is_private": activity.is_private,
        "status": "Ongoing",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    response = supabase.table("activities").insert(new_activity).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create activity")
    return response.data[0]

@router.get("/")
def get_my_activities(
    status: Optional[str] = Query(None, description="Filter by Ongoing or Closed"), 
    current_user: dict = Depends(get_current_fundraiser)
):
    # 1. Search for all activities under this fundraiser's name (excluding those that have been completely deleted).
    query = supabase.table("activities").select("*").eq("fundraiser_id", current_user["user_id"])
    if status:
        query = query.eq("status", status)
    
    response = query.order("created_at", desc=True).execute()
    activities = response.data

    # 2. Core logic: Real-time statistics of the number of bookmarks (Shortlist/Bookmark) for each activity.
    for act in activities:
        # Using count="exact" only retrieves the total number of rows, without fetching specific Donee privacy data, which complies with privacy protection requirements.
        bookmark_count_resp = supabase.table("bookmarks")\
            .select("bookmark_id", count="exact")\
            .eq("activity_id", act["activity_id"])\
            .execute()
            
        # Mount the statistics to the activity fields for return to the frontend
        act["shortlist_count"] = bookmark_count_resp.count if bookmark_count_resp.count is not None else 0
        
    return activities

@router.get("/suggest-target")
def get_suggested_target(
    category_id: int = Query(..., description="The category ID to analyze"),
    current_user: dict = Depends(get_current_fundraiser)
):
    response = supabase.table("activities").select("target_amount").eq("category_id", category_id).eq("status", "Closed").gt("current_amount", 0).execute()
    activities = response.data
    if not activities:
        return {"category_id": category_id, "suggested_target": 500.00, "based_on_records": 0, "message": "Insufficient historical data, using default baseline."}
    
    average_target = round(sum(act["target_amount"] for act in activities) / len(activities), 2)
    return {"category_id": category_id, "suggested_target": average_target, "based_on_records": len(activities), "message": f"Based on {len(activities)} successful campaigns in this category."}

@router.patch("/{activity_id}", response_model=schemas.ActivityResponse)
def update_activity(activity_id: int, update_data: schemas.ActivityUpdate, current_user: dict = Depends(get_current_fundraiser)):
    existing_resp = supabase.table("activities").select("*").eq("activity_id", activity_id).eq("fundraiser_id", current_user["user_id"]).execute()
    if not existing_resp.data:
        raise HTTPException(status_code=404, detail="Activity not found or unauthorized")
    
    if existing_resp.data[0]["status"] == "Closed":
        raise HTTPException(status_code=400, detail="Cannot edit a closed activity")

    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")
        
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    res = supabase.table("activities").update(update_dict).eq("activity_id", activity_id).execute()
    return res.data[0]

@router.post("/{activity_id}/close")
def close_activity(activity_id: int, current_user: dict = Depends(get_current_fundraiser)):
    res = supabase.table("activities").update({"status": "Closed"}).eq("activity_id", activity_id).eq("fundraiser_id", current_user["user_id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Activity not found or unauthorized")
    return {"message": "Activity successfully closed"}

# 🔥 Added: Soft delete / archive interface
@router.post("/{activity_id}/archive")
def archive_activity(activity_id: int, current_user: dict = Depends(get_current_fundraiser)):
    # Update the status to 'Archived' instead of brute-force deleting()
    res = supabase.table("activities").update({"status": "Archived"}).eq("activity_id", activity_id).eq("fundraiser_id", current_user["user_id"]).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Activity not found or unauthorized")
        
    return {"message": "Activity successfully archived"}

#Story 29, 30: Fundraiser query historical activity (filter by date and category)
@router.get("/history")
def get_campaign_history(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    category_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_fundraiser)
):
    """Story 29 & 30: Search History by Date and Category"""
    # Only query activities under the current fundraiser's name with a 'Closed' status
    query = supabase.table("activities").select("*, categories(name)").eq("fundraiser_id", current_user["user_id"]).eq("status", "Closed")
    
    if category_id:
        query = query.eq("category_id", category_id)
    if start_date:
        query = query.gte("created_at", f"{start_date}T00:00:00Z")
    if end_date:
        query = query.lte("created_at", f"{end_date}T23:59:59Z")
        
    return query.order("created_at", desc=True).execute().data

@router.post("/{activity_id}/reports")
def create_progress_report(activity_id: int, report: schemas.ProgressReportCreate, current_user: dict = Depends(get_current_fundraiser)):
    """Fundraiser Release a progress report (providing data for Story 32)"""
    # Verify if you are the owner of this activity.
    act = supabase.table("activities").select("activity_id").eq("activity_id", activity_id).eq("fundraiser_id", current_user["user_id"]).execute()
    if not act.data:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    new_report = {
        "activity_id": activity_id,
        "title": report.title,
        "content": report.content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    res = supabase.table("progress_reports").insert(new_report).execute()
    return res.data[0]