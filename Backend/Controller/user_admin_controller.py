# Controller/user_admin_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, EmailStr

# Import role authentication dependencies
from dependencies import get_user_admin

# Import Entities (these Entity classes have already handled Supabase/Database connections)
from Entities.user_account import UserAccountEntity, UserAccountCreate
from Entities.user_profile import UserProfileEntity, UserProfileCreate, UserProfileUpdate

router = APIRouter(prefix="/user-admin", tags=["User Admin Controller (BCE Class Mode)"])

# Temporary request model
class EmailUpdate(BaseModel):
    new_email: EmailStr

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

# =======================================
# --- Profile Management (Story 1-5) ---
# =======================================

class CreateUserProfileController:
    def execute(self, profile_data: UserProfileCreate):
        """Story 1: Create a user profile"""
        profile, error = UserProfileEntity.create_profile(profile_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Profile created successfully.", "profile": profile}

class ViewUserProfileController:
    def execute(self, user_id: int):
        """Story 2: View user profile"""
        profile, error = UserProfileEntity.get_profile(user_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return profile

class UpdateUserProfileController:
    def execute(self, user_id: int, update_data: UserProfileUpdate):
        """Story 3: Update user profile"""
        profile, error = UserProfileEntity.update_profile(user_id, update_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Profile updated.", "profile": profile}

class SuspendUserProfileController:
    def execute(self, user_id: int):
        """Story 4: Suspend user profile"""
        result, error = UserProfileEntity.suspend_profile(user_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return result

class SearchUserProfileController:
    def execute(self, username: Optional[str]):
        """Story 5: Search user profiles"""
        profiles, error = UserProfileEntity.search_profiles(username)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return profiles

# =======================================
# --- Account Management (Story 6-10) ---
# =======================================
class CreateUserAccountController:
    def execute(self, account_data: UserAccountCreate):
        """Story 6: Create a user account"""
        account, error = UserAccountEntity.create_account(account_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {
            "message": "Account created. Proceed to Story 1.",
            "account_id": account["user_id"],
            "email": account["email"]
        }

class ViewUserAccountController:
    def execute(self, user_id: int):
        """Story 7: View user account"""
        account, error = UserAccountEntity.get_account(user_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return account

class UpdateUserAccountController:
    def execute(self, user_id: int, new_email: str):
        """Story 8: Update user account"""
        account, error = UserAccountEntity.update_account(user_id, new_email)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Account updated.", "account": account}

class SuspendUserAccountController:
    def execute(self, user_id: int):
        """Story 9: Suspend user account"""
        account, error = UserAccountEntity.suspend_account(user_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Account suspended.", "account": account}

class SearchUserAccountController:
    def execute(self, email: Optional[str]):
        """Story 10: Search user accounts"""
        accounts, error = UserAccountEntity.search_accounts(email)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return accounts


# ============================================================
# Instantiate these classes and call
# ============================================================

# --- Profiles ---
@router.post("/profiles")
def route_create_profile(data: UserProfileCreate, admin=Depends(get_user_admin)):
    return CreateUserProfileController().execute(data)

@router.get("/profiles/{user_id}")
def route_view_profile(user_id: int, admin=Depends(get_user_admin)):
    return ViewUserProfileController().execute(user_id)

@router.patch("/profiles/{user_id}")
def route_update_profile(user_id: int, data: UserProfileUpdate, admin=Depends(get_user_admin)):
    return UpdateUserProfileController().execute(user_id, data)

@router.post("/profiles/{user_id}/suspend")
def route_suspend_profile(user_id: int, admin=Depends(get_user_admin)):
    return SuspendUserProfileController().execute(user_id)

@router.get("/profiles")
def route_search_profiles(username: Optional[str] = Query(None), admin=Depends(get_user_admin)):
    return SearchUserProfileController().execute(username)

# --- Accounts ---
@router.post("/accounts")
def route_create_account(data: UserAccountCreate, admin=Depends(get_user_admin)):
    return CreateUserAccountController().execute(data)

@router.get("/accounts/{user_id}")
def route_view_account(user_id: int, admin=Depends(get_user_admin)):
    return ViewUserAccountController().execute(user_id)

@router.patch("/accounts/{user_id}")
def route_update_account(user_id: int, email: str = Query(...), admin=Depends(get_user_admin)):
    return UpdateUserAccountController().execute(user_id, email)

@router.post("/accounts/{user_id}/suspend")
def route_suspend_account(user_id: int, admin=Depends(get_user_admin)):
    return SuspendUserAccountController().execute(user_id)

@router.get("/accounts")
def route_search_accounts(email: Optional[str] = Query(None), admin=Depends(get_user_admin)):
    return SearchUserAccountController().execute(email)