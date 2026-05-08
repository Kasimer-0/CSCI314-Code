from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, EmailStr

from dependencies import get_donee
# Import Entities (these Entity classes have already handled Supabase/Database connections)
from Entities.user_account import UserAccountEntity
from Entities.donee_activity import DoneeActivityEntity
from Entities.donee_favorite import FavoriteEntity
from Entities.donation import DonationEntity, DonationRequest

router = APIRouter(prefix="/donee", tags=["Donee Controller (BCE Class Mode)"])

class DoneeLoginRequest(BaseModel):
    email: EmailStr
    password: str

# ============================================================
# --- Controller Classes (Story 24 - 32) ---
# ============================================================

class LoginDoneeController:
    def execute(self, login_data: DoneeLoginRequest):
        """Story 29: Login to my account"""
        token_response, error = UserAccountEntity.login_donee(login_data)
        if error:
            status_code = 401 if "Incorrect" in error else 403
            raise HTTPException(status_code=status_code, detail=error)
        return token_response

class LogoutDoneeController:
    def execute(self):
        """Story 30: Logout of my account"""
        result, _ = UserAccountEntity.logout_donee()
        return result

class SearchActivitiesController:
    def execute(self, title: Optional[str]):
        """Story 24: Search for fundraising activities"""
        activities, error = DoneeActivityEntity.search_activities(title)
        if error: raise HTTPException(status_code=500, detail=error)
        return activities

class ViewActivityController:
    def execute(self, activity_id: int):
        """Story 25: View fundraising activity details"""
        activity, error = DoneeActivityEntity.get_activity(activity_id)
        if error: raise HTTPException(status_code=404, detail=error)
        return activity

class ToggleFavoriteController:
    def execute(self, activity_id: int, profile_id: int):
        """Story 26: Save/Remove activity to favorites"""
        result, error = FavoriteEntity.toggle_favorite(activity_id, profile_id)
        if error: raise HTTPException(status_code=400, detail=error)
        return result

class ManageFavoritesController:
    def execute(self, profile_id: int, title: Optional[str]):
        """Story 27 & 28: Search and view my favorite activities"""
        favorites, error = FavoriteEntity.get_favorites(profile_id, title)
        if error: raise HTTPException(status_code=500, detail=error)
        return favorites

class DonateToActivityController:
    def execute(self, activity_id: int, profile_id: int, donation_data: DonationRequest):
        """Core Feature: Make a donation to an activity"""
        result, error = DonationEntity.donate_to_activity(activity_id, profile_id, donation_data)
        if error: raise HTTPException(status_code=400, detail=error)
        return result

class SearchPastDonationsController:
    def execute(self, profile_id: int, title: Optional[str]):
        """Story 31: Search for my past donations"""
        donations, error = DonationEntity.search_past_donations(profile_id, title)
        if error: raise HTTPException(status_code=500, detail=error)
        return donations

class ViewPastDonationController:
    def execute(self, donation_id: int, profile_id: int):
        """Story 32: View my past donation details"""
        donation, error = DonationEntity.view_past_donation_detail(donation_id, profile_id)
        if error: raise HTTPException(status_code=404, detail=error)
        return donation


# ============================================================
# Route Binding: Instantiate Classes and Execute
# ============================================================

@router.post("/login")
def route_donee_login(login_data: DoneeLoginRequest):
    """API for Story 29"""
    return LoginDoneeController().execute(login_data)

@router.post("/logout")
def route_donee_logout(donee_user = Depends(get_donee)):
    """API for Story 30"""
    return LogoutDoneeController().execute()

@router.get("/activities")
def route_search_activities(title: Optional[str] = Query(None), donee_user = Depends(get_donee)):
    """API for Story 24"""
    return SearchActivitiesController().execute(title)

@router.get("/activities/{activity_id}")
def route_view_activity(activity_id: int, donee_user = Depends(get_donee)):
    """API for Story 25"""
    return ViewActivityController().execute(activity_id)

@router.post("/favorites/{activity_id}")
def route_save_favorite(activity_id: int, donee_user = Depends(get_donee)):
    """API for Story 26"""
    return ToggleFavoriteController().execute(activity_id, donee_user.profile.profile_id)

@router.get("/favorites")
def route_manage_favorites(title: Optional[str] = Query(None), donee_user = Depends(get_donee)):
    """API for Story 27 & 28"""
    return ManageFavoritesController().execute(donee_user.profile.profile_id, title)

@router.post("/activities/{activity_id}/donate")
def route_donate_to_activity(activity_id: int, donation_data: DonationRequest, donee_user = Depends(get_donee)):
    """API for Donation execution"""
    return DonateToActivityController().execute(activity_id, donee_user.profile.profile_id, donation_data)

@router.get("/donations")
def route_search_past_donations(title: Optional[str] = Query(None), donee_user = Depends(get_donee)):
    """API for Story 31"""
    return SearchPastDonationsController().execute(donee_user.profile.profile_id, title)

@router.get("/donations/{donation_id}")
def route_view_past_donation(donation_id: int, donee_user = Depends(get_donee)):
    """API for Story 32"""
    return ViewPastDonationController().execute(donation_id, donee_user.profile.profile_id)