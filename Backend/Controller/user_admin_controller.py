from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, EmailStr

# Import role authentication dependencies
from dependencies import get_user_admin

# Import Entities (These handle the DB logic)
from Entities.user_account import UserAccount, UserAccountCreate
from Entities.user_profile import UserProfile, ProfileCreate, ProfileUpdate

router = APIRouter(prefix="/user-admin", tags=["User Admin Controller (BCE Class Mode)"])

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

# =======================================
# --- Profile Management (Story 1-5) ---
# =======================================

class CreateUserProfileController:
    def execute(self, profile_data: ProfileCreate):
        """Story 1: Create a user profile"""
        profile, error = UserProfile.create_profile(profile_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Profile created successfully.", "profile": profile}

class ViewUserProfileController:
    def execute(self, profile_id: int):
        """Story 2: View user profile"""
        profile, error = UserProfile.get_profile(profile_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return profile

class UpdateProfileController:
    def execute(self, profile_id: int, prof_data: ProfileUpdate):
        """Story 3: Update profile description"""
        profile, error = UserProfile.update_profile(profile_id, prof_data)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return profile

class SuspendUserProfileController:
    def execute(self, profile_id: int):
        """Story 4: Suspend user profile"""
        profile, error = UserProfile.suspend_profile(profile_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Profile suspended successfully"}

class SearchProfilesController:
    def execute(self, profile_name: Optional[str]):
        """Story 5: Search profiles by profile_name"""
        profiles, error = UserProfile.search_profiles(profile_name)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return profiles

# =======================================
# --- Account Management (Story 6-10) ---
# =======================================
class CreateUserAccountController:
    def execute(self, account_data: UserAccountCreate):
        """Story 6: Create a user account"""
        account, error = UserAccount.create_account(account_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {
            "message": "Account created. Proceed to Story 1.",
            "account_id": account["user_id"],
            "email": account["email"]
        }

class ViewUserAccountController:
    def execute(self, account_id: int):
        """Story 7: View user account"""
        account, error = UserAccount.get_account(account_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return account

class UpdateUserAccountController:
    def execute(self, account_id: int, new_email: str):
        """Story 8: Update user account"""
        account, error = UserAccount.update_account(account_id, new_email)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Account updated.", "account": account}

class SuspendUserAccountController:
    def execute(self, account_id: int):
        """Story 9: Suspend user account"""
        account, error = UserAccount.suspend_account(account_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Account suspended.", "account": account}

class SearchUserAccountController:
    def execute(self, email: Optional[str]):
        """Story 10: Search user accounts"""
        accounts, error = UserAccount.search_accounts(email)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return accounts

# =======================================
# --- Admin Authentication (Story 11 - 12) ---
# =======================================
class AdminLoginController:
    def execute(self, login_data: AdminLoginRequest):
        """Story 11: Login to my user admin account"""
        token_response, error = UserAccount.login_admin(login_data)
        if error:
            status_code = 401 if "Incorrect" in error else 403
            raise HTTPException(status_code=status_code, detail=error)
        return token_response
    
class LogoutUserAdminController:
    def execute(self):
        """Story 12: Logout of my user admin account"""
        result, error = UserAccount.logout_admin()
        if error:
            raise HTTPException(status_code=400, detail=error)
        return result


# ============================================================
# Route Binding: Instantiate Classes and Execute
# ============================================================

# --- Profiles ---
@router.post("/profiles")
def route_create_profile(data: ProfileCreate, admin=Depends(get_user_admin)):
    """API for Story 1"""
    return CreateUserProfileController().execute(data)

@router.get("/profiles/{profile_id}")
def route_view_profile(profile_id: int, admin=Depends(get_user_admin)):
    """API for Story 2"""
    return ViewUserProfileController().execute(profile_id)

@router.patch("/profiles/{profile_id}")
def route_update_profile(profile_id: int, prof_data: ProfileUpdate, admin_user=Depends(get_user_admin)):
    """API for Story 3"""
    return UpdateProfileController().execute(profile_id, prof_data)

@router.post("/profiles/{profile_id}/suspend")
def route_suspend_profile(profile_id: int, admin=Depends(get_user_admin)):
    """API for Story 4"""
    return SuspendUserProfileController().execute(profile_id)

@router.get("/profiles")
def route_search_profiles(profile_name: Optional[str] = Query(None), admin_user=Depends(get_user_admin)):
    """API for Story 5"""
    return SearchProfilesController().execute(profile_name)

# --- Accounts ---
@router.post("/login")
def route_admin_login(login_data: AdminLoginRequest):
    """API for Story 11"""
    return AdminLoginController().execute(login_data)

@router.post("/logout")
def route_admin_logout(admin=Depends(get_user_admin)):
    """API for Story 12"""
    return LogoutUserAdminController().execute()

@router.post("/accounts")
def route_create_account(data: UserAccountCreate, admin=Depends(get_user_admin)):
    """API for Story 6"""
    return CreateUserAccountController().execute(data)

@router.get("/accounts/{account_id}")
def route_view_account(account_id: int, admin=Depends(get_user_admin)):
    """API for Story 7"""
    return ViewUserAccountController().execute(account_id)

@router.patch("/accounts/{account_id}")
def route_update_account(account_id: int, email: str = Query(...), admin=Depends(get_user_admin)):
    """API for Story 8"""
    return UpdateUserAccountController().execute(account_id, email)

@router.post("/accounts/{account_id}/suspend")
def route_suspend_account(account_id: int, admin=Depends(get_user_admin)):
    """API for Story 9"""
    return SuspendUserAccountController().execute(account_id)

@router.get("/accounts")
def route_search_accounts(email: Optional[str] = Query(None), admin=Depends(get_user_admin)):
    """API for Story 10"""
    return SearchUserAccountController().execute(email)