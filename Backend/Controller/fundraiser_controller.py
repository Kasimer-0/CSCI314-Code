# Controller/fundraiser_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies import get_db, get_fundraiser
from Entities.fundraising_activity import FundraisingActivityEntity, ActivityCreate

router = APIRouter(prefix="/fundraiser", tags=["Fundraiser Controller"])

@router.post("/activities")
def create_fundraising_activity(activity_data: ActivityCreate, db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 13: Create a fundraising activity"""
    activity, error = FundraisingActivityEntity.create_activity(db, activity_data, fr_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return activity

@router.get("/activities/{activity_id}")
def view_fundraising_activity(activity_id: int, db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 14: View my fundraising activity"""
    activity, error = FundraisingActivityEntity.get_activity(db, activity_id, fr_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return activity

@router.patch("/activities/{activity_id}")
def update_fundraising_activity(activity_id: int, title: str, db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 15: Update my fundraising activity"""
    activity, error = FundraisingActivityEntity.update_activity(db, activity_id, title, fr_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return activity

@router.post("/activities/{activity_id}/suspend")
def suspend_fundraising_activity(activity_id: int, db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 16: Suspend fundraising activity"""
    activity, error = FundraisingActivityEntity.suspend_activity(db, activity_id, fr_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Activity suspended successfully.", "activity": activity}

@router.get("/activities")
def search_fundraising_activities(title: Optional[str] = Query(None), db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 17: Search for fundraising activities"""
    activities, error = FundraisingActivityEntity.search_activities(db, title, fr_user.profile.profile_id)
    return activities

@router.get("/history")
def search_past_activities(title: Optional[str] = Query(None), db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 22: Search for the history of past fundraising activities"""
    history, error = FundraisingActivityEntity.search_history(db, title, fr_user.profile.profile_id)
    return history

@router.get("/history/{activity_id}")
def view_past_activity(activity_id: int, db: Session = Depends(get_db), fr_user = Depends(get_fundraiser)):
    """Story 23: View past fundraising activity"""
    activity, error = FundraisingActivityEntity.get_activity(db, activity_id, fr_user.profile.profile_id)
    if error or activity.status != "Closed":
        raise HTTPException(status_code=404, detail="Past activity not found.")
    return activity