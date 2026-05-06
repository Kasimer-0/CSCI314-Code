# Controller/user_admin_controller.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr

# Importing dependencies for database session and admin authentication
from dependencies import get_db, get_user_admin

# Importing Entity classes for User Account and Profile management
from Entities.user_account import UserAccountEntity, UserAccountCreate
from Entities.user_profile import UserProfileEntity, UserProfileCreate, UserProfileUpdate

router = APIRouter(prefix="/user-admin", tags=["User Admin (Story 1-12)"])

# Temporary Request Body Models (for receiving single field updates or login data)
class EmailUpdate(BaseModel):
    new_email: EmailStr

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

# ==========================================
# User Profile Management (Story 1 - 5)
# ==========================================

@router.post("/profiles")
def create_user_profile(
    profile_data: UserProfileCreate, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 1: Create User Profile"""
    profile, error = UserProfileEntity.create_profile(db, profile_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return profile

@router.get("/profiles/{profile_id}")
def view_user_profile(
    profile_id: int, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 2: View User Profile"""
    profile, error = UserProfileEntity.get_profile(db, profile_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return profile

@router.put("/profiles/{profile_id}")
def update_user_profile(
    profile_id: int, 
    update_data: UserProfileUpdate, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 3: Update User Profile"""
    profile, error = UserProfileEntity.update_profile(db, profile_id, update_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return profile

@router.patch("/profiles/{profile_id}/suspend")
def suspend_user_profile(
    profile_id: int, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 4: Suspend User Profile"""
    profile, error = UserProfileEntity.get_profile(db, profile_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    account, err = UserAccountEntity.suspend_account(db, profile.account_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"message": f"Profile and associated Account {profile.account_id} suspended successfully"}

@router.get("/profiles")
def search_user_profiles(
    username: Optional[str] = None, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 5: Search User Profiles"""
    profiles, error = UserProfileEntity.search_profiles(db, username)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return profiles


# ==========================================
# User Account Management (Story 6 - 10)
# ==========================================

@router.post("/accounts")
def create_user_account(
    account_data: UserAccountCreate, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 6: Create User Account"""
    account, error = UserAccountEntity.create_account(db, account_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return account

@router.get("/accounts/{account_id}")
def view_user_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 7: View User Account"""
    account, error = UserAccountEntity.get_account(db, account_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return account

@router.put("/accounts/{account_id}")
def update_user_account(
    account_id: int, 
    email_data: EmailUpdate, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 8: Update User Account"""
    account, error = UserAccountEntity.update_account(db, account_id, email_data.new_email)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return account

@router.patch("/accounts/{account_id}/suspend")
def suspend_user_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 9: Suspend User Account"""
    account, error = UserAccountEntity.suspend_account(db, account_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"message": f"Account {account_id} suspended successfully"}

@router.get("/accounts")
def search_user_accounts(
    email: Optional[str] = None, 
    db: Session = Depends(get_db), 
    admin_user = Depends(get_user_admin)
):
    """Story 10: Search User Accounts"""
    accounts, error = UserAccountEntity.search_accounts(db, email)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return accounts


# ==========================================
# Admin Self Authentication (Story 11 - 12)
# ==========================================

@router.post("/login")
def login_admin(login_data: AdminLoginRequest, db: Session = Depends(get_db)):
    """Story 11: Login to user admin account"""
    import jwt
    from datetime import datetime, timedelta, timezone
    from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

    account = UserAccountEntity.get_user_by_email_for_auth(db, login_data.email)
    
    if not account or not UserAccountEntity.verify_password(login_data.password, account.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not account.profile or account.profile.role_id != 0:
        raise HTTPException(status_code=403, detail="Access denied. Only User Admins can log in here.")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": account.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
def logout_admin(admin_user = Depends(get_user_admin)):
    """Story 12: Logout of user admin account"""
    return {"message": "Successfully logged out. Please remove token from client storage."}