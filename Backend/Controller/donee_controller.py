# Controller/donee_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies import get_db, get_donee
from Entities.donee_action import DoneeEntity, DonationRequest, DoneeLoginRequest, DoneeToken

router = APIRouter(prefix="/donee", tags=["Donee Controller"])

@router.post("/login", response_model=DoneeToken)
def donee_login(login_data: DoneeLoginRequest, db: Session = Depends(get_db)):
    """Story 29: Login to my account (Donee Exclusive)"""
    token_response, error = DoneeEntity.login_donee(db, login_data)
    if error:
        status_code = 401 if "Incorrect" in error else 403
        raise HTTPException(status_code=status_code, detail=error)
    return token_response

@router.post("/logout")
def donee_logout(donee_user = Depends(get_donee)):
    """Story 30: Logout of my account (Donee Exclusive)"""
    return {"message": "Successfully logged out. Please discard your token."}

@router.get("/activities")
def search_fundraising_activities(title: Optional[str] = Query(None), db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Story 24: Search for fundraising activities"""
    activities, error = DoneeEntity.search_activities(db, title)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return activities

@router.get("/activities/{activity_id}")
def view_fundraising_activity(activity_id: int, db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Story 25: View fundraising activity"""
    activity, error = DoneeEntity.view_activity(db, activity_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return activity

@router.post("/favorites/{activity_id}")
def save_activity_to_favorites(activity_id: int, db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Story 26: Save fundraising activity into favourites list"""
    result, error = DoneeEntity.toggle_favorite(db, activity_id, donee_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/favorites")
def manage_favourite_list(title: Optional[str] = Query(None), db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Story 27 & 28: Search and View favourite list"""
    favorites, error = DoneeEntity.get_favorites(db, donee_user.profile.profile_id, title)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return favorites

@router.post("/activities/{activity_id}/donate")
def donate_to_activity(activity_id: int, donation_data: DonationRequest, db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Helper: Execute a donation"""
    result, error = DoneeEntity.make_donation(db, activity_id, donee_user.profile.profile_id, donation_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/donations")
def search_past_donations(db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Story 31: Search for my past donations"""
    donations, error = DoneeEntity.search_past_donations(db, donee_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return donations

@router.get("/donations/{donation_id}")
def view_past_donation(donation_id: int, db: Session = Depends(get_db), donee_user = Depends(get_donee)):
    """Story 32: View my past donation"""
    donation_detail, error = DoneeEntity.view_past_donation_detail(db, donation_id, donee_user.profile.profile_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return donation_detail