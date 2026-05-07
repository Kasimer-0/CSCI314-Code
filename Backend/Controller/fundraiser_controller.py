# Controller/fundraiser_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from dependencies import get_fundraiser
from Entities.fundraising_activity import FundraisingActivityEntity, ActivityCreate

router = APIRouter(prefix="/fundraiser", tags=["Fundraiser Controller (BCE Class Mode)"])

# ============================================================
# --- Controller Classes （Story 13 - 23）---
# ============================================================

class CreateFundraisingActivityController:
    def execute(self, activity_data: ActivityCreate, profile_id: int):
        """Story 13: Create a fundraising activity"""
        activity, error = FundraisingActivityEntity.create_activity(activity_data, profile_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return activity

class ViewFundraisingActivityController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 14: View my fundraising activity"""
        activity, error = FundraisingActivityEntity.get_activity(activity_id, profile_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return activity

class UpdateFundraisingActivityController:
    def execute(self, activity_id: int, title: str, profile_id: int):
        """Story 15: Update my fundraising activity"""
        activity, error = FundraisingActivityEntity.update_activity(activity_id, title, profile_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return activity

class SuspendFundraisingActivityController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 16: Suspend fundraising activity"""
        activity, error = FundraisingActivityEntity.suspend_activity(activity_id, profile_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Activity suspended successfully.", "activity": activity}

class SearchFundraisingActivitiesController:
    def execute(self, title: Optional[str], profile_id: int):
        """Story 17: Search for fundraising activities"""
        activities, error = FundraisingActivityEntity.search_activities(title, profile_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return activities

class SearchPastActivitiesController:
    def execute(self, title: Optional[str], profile_id: int):
        """Story 22: Search for the history of past fundraising activities"""
        history, error = FundraisingActivityEntity.search_history(title, profile_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return history

class ViewPastActivityController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 23: View past fundraising activity"""
        activity, error = FundraisingActivityEntity.get_activity(activity_id, profile_id)
        if error or activity.status != "Closed":
            raise HTTPException(status_code=404, detail="Past activity not found.")
        return activity


# ============================================================
# Route binding: Instantiate these classes and call execute()
# ============================================================

@router.post("/activities")
def route_create_fundraising_activity(activity_data: ActivityCreate, fr_user=Depends(get_fundraiser)):
    return CreateFundraisingActivityController().execute(activity_data, fr_user.profile.profile_id)

@router.get("/activities/{activity_id}")
def route_view_fundraising_activity(activity_id: int, fr_user=Depends(get_fundraiser)):
    return ViewFundraisingActivityController().execute(activity_id, fr_user.profile.profile_id)

@router.patch("/activities/{activity_id}")
def route_update_fundraising_activity(activity_id: int, title: str, fr_user=Depends(get_fundraiser)):
    return UpdateFundraisingActivityController().execute(activity_id, title, fr_user.profile.profile_id)

@router.post("/activities/{activity_id}/suspend")
def route_suspend_fundraising_activity(activity_id: int, fr_user=Depends(get_fundraiser)):
    return SuspendFundraisingActivityController().execute(activity_id, fr_user.profile.profile_id)

@router.get("/activities")
def route_search_fundraising_activities(title: Optional[str] = Query(None), fr_user=Depends(get_fundraiser)):
    return SearchFundraisingActivitiesController().execute(title, fr_user.profile.profile_id)

@router.get("/history")
def route_search_past_activities(title: Optional[str] = Query(None), fr_user=Depends(get_fundraiser)):
    return SearchPastActivitiesController().execute(title, fr_user.profile.profile_id)

@router.get("/history/{activity_id}")
def route_view_past_activity(activity_id: int, fr_user=Depends(get_fundraiser)):
    return ViewPastActivityController().execute(activity_id, fr_user.profile.profile_id)