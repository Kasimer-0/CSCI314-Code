from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, EmailStr

from dependencies import get_fundraiser

# Import the two split Entities
from Entities.user_account import UserAccountEntity
from Entities.fundraising_activity import FundraisingActivityEntity, ActivityCreate

router = APIRouter(prefix="/fundraiser", tags=["Fundraiser Controller (BCE Class Mode)"])

# Place the Pydantic model for Login in the Controller layer (because it represents the input format of the request).
class FundraiserLoginRequest(BaseModel):
    email: EmailStr
    password: str

# ============================================================
# --- 1. Authentication related Controllers (Story 13 - 23) ---
# ============================================================

class LoginFundraiserController:
    def execute(self, login_data: FundraiserLoginRequest):
        """Story 18: Login to my account"""
        # Call the Account Entity to handle login.
        token_response, error = UserAccountEntity.login_fundraiser(login_data)
        if error:
            status_code = 401 if "Incorrect" in error else 403
            raise HTTPException(status_code=status_code, detail=error)
        return token_response

class LogoutFundraiserController:
    def execute(self):
        """Story 19: Logout of my account"""
        # Call the Account Entity to handle logout
        result, _ = UserAccountEntity.logout_fundraiser()
        return result

class CreateFundraisingActivityController:
    def execute(self, activity_data: ActivityCreate, profile_id: int):
        """Story 13: Create a fundraising activity"""
        # Call the Activity Entity to handle the activity creation
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
            raise HTTPException(status_code=400, detail=error)
        return activities

class TrackActivityViewsController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 20: Track the number of views"""
        stats, error = FundraisingActivityEntity.get_activity_views(activity_id, profile_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return stats

class TrackActivityShortlistsController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 21: Track the number of shortlists"""
        stats, error = FundraisingActivityEntity.get_activity_shortlists(activity_id, profile_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return stats

class SearchPastActivitiesController:
    def execute(self, title: Optional[str], profile_id: int):
        """Story 22: Search for the history of past fundraising activities"""
        history, error = FundraisingActivityEntity.search_history(title, profile_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return history

class ViewPastActivityController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 23: View past fundraising activity"""
        activity, error = FundraisingActivityEntity.get_activity(activity_id, profile_id)
        # History records include Closed and Suspended states.
        if error or activity.status not in ["Closed", "Suspended"]:
            raise HTTPException(status_code=404, detail="No such historical activity was found.")
        return activity

# ============================================================
# Route Binding: Instantiate Classes and Execute
# ============================================================

@router.post("/login")
def route_fundraiser_login(login_data: FundraiserLoginRequest):
    """API for Story 18"""
    return LoginFundraiserController().execute(login_data)

@router.post("/logout")
def route_fundraiser_logout(fr_user=Depends(get_fundraiser)):
    """API for Story 19"""
    return LogoutFundraiserController().execute()

@router.post("/activities")
def route_create_fundraising_activity(activity_data: ActivityCreate, fr_user=Depends(get_fundraiser)):
    """API for Story 13"""
    return CreateFundraisingActivityController().execute(activity_data, fr_user.profile.profile_id)

@router.get("/activities/{activity_id}")
def route_view_fundraising_activity(activity_id: int, fr_user=Depends(get_fundraiser)):
    """API for Story 14"""
    return ViewFundraisingActivityController().execute(activity_id, fr_user.profile.profile_id)

@router.patch("/activities/{activity_id}")
def route_update_fundraising_activity(activity_id: int, title: str, fr_user=Depends(get_fundraiser)):
    """API for Story 15"""
    return UpdateFundraisingActivityController().execute(activity_id, title, fr_user.profile.profile_id)

@router.post("/activities/{activity_id}/suspend")
def route_suspend_fundraising_activity(activity_id: int, fr_user=Depends(get_fundraiser)):
    """API for Story 16"""
    return SuspendFundraisingActivityController().execute(activity_id, fr_user.profile.profile_id)

@router.get("/activities")
def route_search_fundraising_activities(title: Optional[str] = Query(None), fr_user=Depends(get_fundraiser)):
    """API for Story 17"""
    return SearchFundraisingActivitiesController().execute(title, fr_user.profile.profile_id)

@router.get("/activities/{activity_id}/views")
def route_track_activity_views(activity_id: int, fr_user=Depends(get_fundraiser)):
    """API for Story 20"""
    return TrackActivityViewsController().execute(activity_id, fr_user.profile.profile_id)

@router.get("/activities/{activity_id}/shortlists")
def route_track_activity_shortlists(activity_id: int, fr_user=Depends(get_fundraiser)):
    """API for Story 21"""
    return TrackActivityShortlistsController().execute(activity_id, fr_user.profile.profile_id)

@router.get("/history")
def route_search_past_activities(title: Optional[str] = Query(None), fr_user=Depends(get_fundraiser)):
    """API for Story 22"""
    return SearchPastActivitiesController().execute(title, fr_user.profile.profile_id)

@router.get("/history/{activity_id}")
def route_view_past_activity(activity_id: int, fr_user=Depends(get_fundraiser)):
    """API for Story 23"""
    return ViewPastActivityController().execute(activity_id, fr_user.profile.profile_id)

@router.get("/activities/{activity_id}/stats")
def route_get_activity_stats(activity_id: int, fr_user=Depends(get_fundraiser)):
    """API for Story 24"""
    # Can combine existing logic from within an Entity.
    views, _ = FundraisingActivityEntity.get_activity_views(activity_id, fr_user.profile.profile_id)
    shortlists, _ = FundraisingActivityEntity.get_activity_shortlists(activity_id, fr_user.profile.profile_id)
    return {
        "title": views["title"],
        "views": views["views"],
        "shortlisted_times": shortlists["shortlisted_times"]
    }