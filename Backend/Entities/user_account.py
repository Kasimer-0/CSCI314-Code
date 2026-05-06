# Entities/user_account.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
import bcrypt
from database import supabase

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class UserAccountCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class UserAccountEntity:
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def create_account(account_data: UserAccountCreate):
        """Entity Logic (Story 6): Insert new account into database"""
        existing = supabase.table("users").select("user_id").eq("email", account_data.email).execute()
        if existing.data:
            return None, "Email already registered in the system."

        hashed_password = UserAccountEntity.get_password_hash(account_data.password)

        new_account = {
            "email": account_data.email,
            "password_hash": hashed_password,
            "status": "Pending", 
            "username": "Pending Setup",   # Placeholder for Profile setup
            "role_id": 1,                  # Default role placeholder
            "is_suspended": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        res = supabase.table("users").insert(new_account).execute()
        if not res.data:
            return None, "Failed to create user account."
        return res.data[0], None

    @staticmethod
    def get_account(user_id: int):
        """Entity Logic (Story 7): View specific user account"""
        res = supabase.table("users").select("user_id, email, role_id, status").eq("user_id", user_id).execute()
        if not res.data:
            return None, "User account not found."
        return res.data[0], None

    @staticmethod
    def update_account(user_id: int, new_email: str):
        """Entity Logic (Story 8): Update user email"""
        res = supabase.table("users").update({"email": new_email}).eq("user_id", user_id).execute()
        if not res.data:
            return None, "Failed to update account or user not found."
        return res.data[0], None

    @staticmethod
    def suspend_account(user_id: int):
        """Entity Logic (Story 9): Suspend user account"""
        res = supabase.table("users").update({"status": "Suspended", "is_suspended": True}).eq("user_id", user_id).execute()
        if not res.data:
            return None, "Failed to suspend account."
        return res.data[0], None

    @staticmethod
    def search_accounts(email_query: Optional[str]):
        """Entity Logic (Story 10): Search user accounts"""
        query = supabase.table("users").select("user_id, email, role_id, status")
        if email_query:
            query = query.ilike("email", f"%{email_query}%")
        res = query.execute()
        return res.data, None
    
    @staticmethod
    def get_user_by_email_for_auth(email: str):
        """Entity Logic: Helper for Token validation in dependencies"""
        res = supabase.table("users").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None