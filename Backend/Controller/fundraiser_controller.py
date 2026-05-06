# Controller/fundraiser_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from dependencies import get_fundraiser

# 导入刚才写好的 Entity
from Entities.fundraising_activity import FundraisingActivityEntity, ActivityCreate

router = APIRouter(prefix="/fundraiser", tags=["Fundraiser Controller"])

# --- Create a fundraising activity (Story 13) ---
@router.post("/activities")
def create_fundraising_activity(activity_data: ActivityCreate, fr: dict = Depends(get_fundraiser)):
    """Story 13: Create a fundraising activity"""
    
    # Controller 核心：只调用 Entity 方法
    activity, error = FundraisingActivityEntity.create_activity(activity_data, fr["user_id"])
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    return activity


# --- View my fundraising activity (Story 14) ---
@router.get("/activities/{activity_id}")
def view_fundraising_activity(activity_id: int, fr: dict = Depends(get_fundraiser)):
    """Story 14: View my fundraising activity"""
    
    activity, error = FundraisingActivityEntity.get_activity(activity_id, fr["user_id"])
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    return activity


# --- Update my fundraising activity (Story 15) ---
@router.patch("/activities/{activity_id}")
def update_fundraising_activity(activity_id: int, title: str, fr: dict = Depends(get_fundraiser)):
    """Story 15: Update my fundraising activity"""
    
    activity, error = FundraisingActivityEntity.update_activity(activity_id, title, fr["user_id"])
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    return activity


# --- Suspend fundraising activity (Story 16) ---
@router.post("/activities/{activity_id}/suspend")
def suspend_fundraising_activity(activity_id: int, fr: dict = Depends(get_fundraiser)):
    """Story 16: Suspend fundraising activity"""
    
    activity, error = FundraisingActivityEntity.suspend_activity(activity_id, fr["user_id"])
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Activity suspended successfully.", "activity": activity}


# --- Search for fundraising activities (Story 17) ---
@router.get("/activities")
def search_fundraising_activities(title: Optional[str] = Query(None), fr: dict = Depends(get_fundraiser)):
    """Story 17: Search for fundraising activities"""
    
    activities, error = FundraisingActivityEntity.search_activities(title, fr["user_id"])
    return activities


# --- Search for the history of past fundraising activities (Story 22) ---
@router.get("/history")
def search_past_activities(title: Optional[str] = Query(None), fr: dict = Depends(get_fundraiser)):
    """Story 22: Search for the history of past fundraising activities"""
    
    history, error = FundraisingActivityEntity.search_history(title, fr["user_id"])
    return history


# --- View past fundraising activity (Story 23) ---
@router.get("/history/{activity_id}")
def view_past_activity(activity_id: int, fr: dict = Depends(get_fundraiser)):
    """Story 23: View past fundraising activity"""
    
    # 历史记录复用 get_activity 的逻辑，但在前端可以限制只能展示 Closed 状态的
    activity, error = FundraisingActivityEntity.get_activity(activity_id, fr["user_id"])
    
    if error or activity.get("status") != "Closed":
        raise HTTPException(status_code=404, detail="Past activity not found.")
    return activity