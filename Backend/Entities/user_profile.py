# Entities/user_profile.py

from pydantic import BaseModel
from typing import Optional
from database import supabase

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class UserProfileCreate(BaseModel):
    user_id: int  
    username: str
    phone_number: Optional[str] = None
    role_id: int

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class UserProfileEntity:

    @staticmethod
    def create_profile(profile_data: UserProfileCreate):
        """Entity Logic (Story 1): Link profile data to an existing account"""
        existing_account = supabase.table("users").select("user_id, username").eq("user_id", profile_data.user_id).execute()
        if not existing_account.data:
            return None, "User account not found. Please create an account first."
        
        # If the placeholder is already changed, it means profile exists
        if existing_account.data[0].get("username") and existing_account.data[0].get("username") != "Pending Setup":
            return None, "Profile already exists for this account."

        update_dict = {
            "username": profile_data.username,
            "phone_number": profile_data.phone_number,
            "role_id": profile_data.role_id,
            "status": "Active" # Activate account after profile creation
        }
        res = supabase.table("users").update(update_dict).eq("user_id", profile_data.user_id).execute()
        if not res.data:
            return None, "Failed to create user profile."
        return res.data[0], None

    @staticmethod
    def get_profile(user_id: int):
        """Entity Logic (Story 2): View user profile"""
        res = supabase.table("users").select("user_id, username, phone_number, role_id").eq("user_id", user_id).execute()
        if not res.data:
            return None, "User profile not found."
        return res.data[0], None

    @staticmethod
    def update_profile(user_id: int, update_data: UserProfileUpdate):
        """Entity Logic (Story 3): Update user profile"""
        data_dict = update_data.dict(exclude_unset=True)
        if not data_dict:
            return None, "No data provided for update."

        res = supabase.table("users").update(data_dict).eq("user_id", user_id).execute()
        if not res.data:
            return None, "Failed to update profile."
        return res.data[0], None

    @staticmethod
    def suspend_profile(user_id: int):
        """Entity Logic (Story 4): Suspend user profile (Hide from public view)"""
        # For profiles, we might just flag a specific profile suspension field, 
        # but here we reuse the main suspension logic per standard practice.
        res = supabase.table("users").update({"is_suspended": True}).eq("user_id", user_id).execute()
        if not res.data:
            return None, "Failed to suspend profile."
        return {"message": f"Profile for user {user_id} suspended."}, None

    @staticmethod
    def search_profiles(username_query: Optional[str]):
        """Entity Logic (Story 5): Search user profiles"""
        query = supabase.table("users").select("user_id, username, phone_number, role_id")
        if username_query:
            query = query.ilike("username", f"%{username_query}%")
        res = query.execute()
        return res.data, None