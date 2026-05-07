# Controller/donee_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from dependencies import get_donee
from Entities.donee_action import DoneeEntity, DonationRequest, DoneeLoginRequest, DoneeToken

router = APIRouter(prefix="/donee", tags=["Donee Controller (BCE Class Mode)"])

# ============================================================
# --- Controller Classes （Story 29 - 32 ）---
# ============================================================

class LoginDoneeController:
    def execute(self, login_data: DoneeLoginRequest):
        """Story 29: Login to my account (Donee Exclusive)"""
        token_response, error = DoneeEntity.login_donee(login_data)
        if error:
            status_code = 401 if "Incorrect" in error else 403
            raise HTTPException(status_code=status_code, detail=error)
        return token_response

class LogoutDoneeController:
    def execute(self):
        """Story 30: Logout of my account"""
        return {"message": "Successfully logged out. Please discard your token."}

class SearchActivitiesController:
    def execute(self, title: Optional[str]):
        """Story 24: Search for fundraising activities"""
        activities, error = DoneeEntity.search_activities(title)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return activities

class ViewActivityController:
    def execute(self, activity_id: int):
        """Story 25: View fundraising activity"""
        activity, error = DoneeEntity.view_activity(activity_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return activity

class ToggleFavoriteController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 26: Save fundraising activity into favourites list"""
        result, error = DoneeEntity.toggle_favorite(activity_id, profile_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return result

class ManageFavoritesController:
    def execute(self, profile_id: int, title: Optional[str]):
        """Story 27 & 28: Search and View favourite list"""
        favorites, error = DoneeEntity.get_favorites(profile_id, title)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return favorites

class DonateToActivityController:
    def execute(self, activity_id: int, profile_id: int, donation_data: DonationRequest):
        """Helper: Execute a donation"""
        result, error = DoneeEntity.make_donation(activity_id, profile_id, donation_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return result

class SearchPastDonationsController:
    def execute(self, profile_id: int):
        """Story 31: Search for my past donations"""
        donations, error = DoneeEntity.search_past_donations(profile_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return donations

class ViewPastDonationController:
    def execute(self, donation_id: int, profile_id: int):
        """Story 32: View my past donation"""
        donation_detail, error = DoneeEntity.view_past_donation_detail(donation_id, profile_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return donation_detail


# ============================================================
# Route binding: Instantiate these classes and call execute()
# ============================================================

@router.post("/login", response_model=DoneeToken)
def route_donee_login(login_data: DoneeLoginRequest):
    return LoginDoneeController().execute(login_data)

@router.post("/logout")
def route_donee_logout(donee_user = Depends(get_donee)):
    return LogoutDoneeController().execute()

@router.get("/activities")
def route_search_activities(title: Optional[str] = Query(None), donee_user = Depends(get_donee)):
    return SearchActivitiesController().execute(title)

@router.get("/activities/{activity_id}")
def route_view_activity(activity_id: int, donee_user = Depends(get_donee)):
    return ViewActivityController().execute(activity_id)

@router.post("/favorites/{activity_id}")
def route_save_favorite(activity_id: int, donee_user = Depends(get_donee)):
    return ToggleFavoriteController().execute(activity_id, donee_user.profile.profile_id)

@router.get("/favorites")
def route_manage_favorites(title: Optional[str] = Query(None), donee_user = Depends(get_donee)):
    return ManageFavoritesController().execute(donee_user.profile.profile_id, title)

@router.post("/activities/{activity_id}/donate")
def route_donate_to_activity(activity_id: int, donation_data: DonationRequest, donee_user = Depends(get_donee)):
    return DonateToActivityController().execute(activity_id, donee_user.profile.profile_id, donation_data)

@router.get("/donations")
def route_search_past_donations(donee_user = Depends(get_donee)):
    return SearchPastDonationsController().execute(donee_user.profile.profile_id)

@router.get("/donations/{donation_id}")
def route_view_past_donation(donation_id: int, donee_user = Depends(get_donee)):
    return ViewPastDonationController().execute(donation_id, donee_user.profile.profile_id)