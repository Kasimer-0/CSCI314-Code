# Controller/user_admin_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from dependencies import get_user_admin

# 引入专属的 Entities
from Entities.user_account import UserAccountEntity, UserAccountCreate
from Entities.user_profile import UserProfileEntity, UserProfileCreate, UserProfileUpdate

router = APIRouter(prefix="/user-admin", tags=["User Admin Controller"])

# ==========================================
# --- User Profile Management (Story 1-5) ---
# ==========================================

@router.post("/profiles")
def create_user_profile(profile_data: UserProfileCreate, admin: dict = Depends(get_user_admin)):
    """Story 1: Create a user profile"""
    profile, error = UserProfileEntity.create_profile(profile_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "User profile created successfully.", "profile": profile}

@router.get("/profiles/{user_id}")
def view_user_profile(user_id: int, admin: dict = Depends(get_user_admin)):
    """Story 2: View user profile"""
    profile, error = UserProfileEntity.get_profile(user_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return profile

@router.patch("/profiles/{user_id}")
def update_user_profile(user_id: int, update_data: UserProfileUpdate, admin: dict = Depends(get_user_admin)):
    """Story 3: Update user profile"""
    profile, error = UserProfileEntity.update_profile(user_id, update_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "User profile updated.", "profile": profile}

@router.post("/profiles/{user_id}/suspend")
def suspend_user_profile(user_id: int, admin: dict = Depends(get_user_admin)):
    """Story 4: Suspend user profile"""
    result, error = UserProfileEntity.suspend_profile(user_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/profiles")
def search_user_profiles(username: Optional[str] = Query(None), admin: dict = Depends(get_user_admin)):
    """Story 5: Search user profiles"""
    profiles, error = UserProfileEntity.search_profiles(username)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return profiles


# ==========================================
# --- User Account Management (Story 6-10) ---
# ==========================================

@router.post("/accounts")
def create_user_account(account_data: UserAccountCreate, admin: dict = Depends(get_user_admin)):
    """Story 6: Create a user account"""
    account, error = UserAccountEntity.create_account(account_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "message": "Account created. Proceed to Story 1 to setup profile.",
        "account_id": account["user_id"],
        "email": account["email"]
    }

@router.get("/accounts/{user_id}")
def view_user_account(user_id: int, admin: dict = Depends(get_user_admin)):
    """Story 7: View user account"""
    account, error = UserAccountEntity.get_account(user_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return account

@router.patch("/accounts/{user_id}")
def update_user_account(user_id: int, new_email: str = Query(..., description="The new email address"), admin: dict = Depends(get_user_admin)):
    """Story 8: Update user account"""
    account, error = UserAccountEntity.update_account(user_id, new_email)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Account updated.", "account": account}

@router.post("/accounts/{user_id}/suspend")
def suspend_user_account(user_id: int, admin: dict = Depends(get_user_admin)):
    """Story 9: Suspend user account"""
    account, error = UserAccountEntity.suspend_account(user_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": "Account suspended successfully.", "account": account}

@router.get("/accounts")
def search_user_accounts(email: Optional[str] = Query(None), admin: dict = Depends(get_user_admin)):
    """Story 10: Search user accounts"""
    accounts, error = UserAccountEntity.search_accounts(email)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return accounts