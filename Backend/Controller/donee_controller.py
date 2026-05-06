# Control/donee_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from dependencies import get_donee

# 引入刚刚创建好的 Donee 专属 Entity 和 Schema
from Entities.donee_action import DoneeEntity, DonationRequest, DoneeLoginRequest, DoneeToken

router = APIRouter(prefix="/donee", tags=["Donee Controller"])

# ==========================================
# --- Login/Logout (Story 29, 30) ---
# ==========================================
@router.post("/login", response_model=DoneeToken)
def donee_login(login_data: DoneeLoginRequest):
    """Story 29: Login to my account (Donee Exclusive)"""
    token_response, error = DoneeEntity.login_donee(login_data)
    if error:
        # 如果包含 Incorrect 则返回 401 认证失败，否则 403 权限拒绝
        status_code = 401 if "Incorrect" in error else 403
        raise HTTPException(status_code=status_code, detail=error)
    return token_response

@router.post("/logout")
def donee_logout():
    """Story 30: Logout of my account (Donee Exclusive)"""
    # 纯后端无状态 JWT Token 注销通常只需要前端丢弃 Token
    return {"message": "Successfully logged out. Please discard your token."}


# ==========================================
# --- Discovery (Story 24, 25, 26, 27, 28) ---
# ==========================================
@router.get("/activities")
def search_fundraising_activities(title: Optional[str] = Query(None, description="Search by activity title"), donee: dict = Depends(get_donee)):
    """Story 24: Search for fundraising activities"""
    activities, error = DoneeEntity.search_activities(title)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return activities

@router.get("/activities/{activity_id}")
def view_fundraising_activity(activity_id: int, donee: dict = Depends(get_donee)):
    """Story 25: View fundraising activity"""
    activity, error = DoneeEntity.view_activity(activity_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return activity

@router.post("/favorites/{activity_id}")
def save_activity_to_favorites(activity_id: int, donee: dict = Depends(get_donee)):
    """Story 26: Save fundraising activity into favourites list"""
    result, error = DoneeEntity.toggle_favorite(activity_id, donee["user_id"])
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/favorites")
def manage_favourite_list(title: Optional[str] = Query(None, description="Search inside favorites"), donee: dict = Depends(get_donee)):
    """Story 27 & 28: Search and View favourite list"""
    favorites, error = DoneeEntity.get_favorites(donee["user_id"], title)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return favorites


# ==========================================
# --- Donations (Story 31, 32 + Helper) ---
# ==========================================
@router.post("/activities/{activity_id}/donate")
def donate_to_activity(activity_id: int, donation_data: DonationRequest, donee: dict = Depends(get_donee)):
    """Helper: Execute a donation (Required to generate data for Story 31 & 32)"""
    result, error = DoneeEntity.make_donation(activity_id, donee["user_id"], donation_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/donations")
def search_past_donations(donee: dict = Depends(get_donee)):
    """Story 31: Search for my past donations"""
    donations, error = DoneeEntity.search_past_donations(donee["user_id"])
    if error:
        raise HTTPException(status_code=500, detail=error)
    return donations

@router.get("/donations/{donation_id}")
def view_past_donation(donation_id: int, donee: dict = Depends(get_donee)):
    """Story 32: View my past donation"""
    donation_detail, error = DoneeEntity.view_past_donation_detail(donation_id, donee["user_id"])
    if error:
        raise HTTPException(status_code=404, detail=error)
    return donation_detail