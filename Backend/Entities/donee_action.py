# Entities/donee_action.py

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import supabase
import bcrypt
import jwt

# 引入 JWT 配置所需的常量
from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class DonationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Donation amount must be strictly positive")
    message: Optional[str] = None
    anonymous: bool = False

class DoneeLoginRequest(BaseModel):
    email: EmailStr
    password: str

class DoneeToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class DoneeEntity:

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """Helper for Story 29"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False

    @staticmethod
    def login_donee(login_data: DoneeLoginRequest):
        """Entity Logic (Story 29): Authenticate Donee and generate token"""
        response = supabase.table("users").select("*").eq("email", login_data.email).execute()
        user = response.data[0] if response.data else None

        if not user or not DoneeEntity.verify_password(login_data.password, user.get("password_hash")):
            return None, "Incorrect email or password."
        
        # 确保只有 Donee (role_id = 1) 能够走这个专用登录通道
        if user.get("role_id") != 1:
            return None, "Access denied. Only Donees can log in here."
            
        if user.get("status") == "Suspended":
            return None, "This account has been suspended."

        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user["email"], "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"access_token": token, "token_type": "bearer"}, None

    @staticmethod
    def search_activities(title: Optional[str]):
        """Entity Logic (Story 24): Search ongoing fundraising activities"""
        query = supabase.table("activities").select("*").eq("status", "Ongoing")
        if title:
            query = query.ilike("title", f"%{title}%")
        res = query.execute()
        return res.data, None

    @staticmethod
    def view_activity(activity_id: int):
        """Entity Logic (Story 25): View specific fundraising activity details"""
        res = supabase.table("activities").select("*, users(username, email)").eq("activity_id", activity_id).execute()
        if not res.data:
            return None, "Activity not found."
        
        activity = res.data[0]
        # (Optional) Update view count
        new_views = activity.get("view_count", 0) + 1
        supabase.table("activities").update({"view_count": new_views}).eq("activity_id", activity_id).execute()
        activity["view_count"] = new_views
        
        return activity, None

    @staticmethod
    def toggle_favorite(activity_id: int, user_id: int):
        """Entity Logic (Story 26): Save/Remove activity to/from favorites list"""
        existing = supabase.table("bookmarks").select("*").eq("user_id", user_id).eq("activity_id", activity_id).execute()
        
        if existing.data:
            supabase.table("bookmarks").delete().eq("bookmark_id", existing.data[0]["bookmark_id"]).execute()
            return {"message": "Activity removed from favorites", "is_bookmarked": False}, None
        else:
            new_bookmark = {
                "user_id": user_id,
                "activity_id": activity_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            supabase.table("bookmarks").insert(new_bookmark).execute()
            return {"message": "Activity saved to favorites", "is_bookmarked": True}, None

    @staticmethod
    def get_favorites(user_id: int, title_query: Optional[str] = None):
        """Entity Logic (Story 27 & 28): View and Search favourite list"""
        query = supabase.table("bookmarks").select("bookmark_id, created_at, activities(*)").eq("user_id", user_id)
        res = query.execute()
        favorites = res.data
        if title_query and favorites:
            favorites = [fav for fav in favorites if title_query.lower() in fav.get("activities", {}).get("title", "").lower()]
        return favorites, None

    @staticmethod
    def make_donation(activity_id: int, user_id: int, donation_data: DonationRequest):
        """Entity Logic: Helper to process a new donation"""
        act_res = supabase.table("activities").select("current_amount, status").eq("activity_id", activity_id).execute()
        if not act_res.data:
            return None, "Activity not found."
            
        activity = act_res.data[0]
        if activity["status"] != "Ongoing":
            return None, "This activity is closed and no longer accepts donations."
            
        new_amount = float(activity.get("current_amount") or 0) + donation_data.amount
        supabase.table("activities").update({"current_amount": new_amount}).eq("activity_id", activity_id).execute()
        
        new_donation = {
            "activity_id": activity_id, 
            "user_id": user_id, 
            "amount": donation_data.amount, 
            "message": donation_data.message, 
            "is_anonymous": donation_data.anonymous, 
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        res = supabase.table("donations").insert(new_donation).execute()
        return {"message": "Donation successful", "new_amount": new_amount, "donation_record": res.data[0]}, None

    @staticmethod
    def search_past_donations(user_id: int):
        """Entity Logic (Story 31): Search for past donations"""
        res = supabase.table("donations").select("donation_id, amount, created_at, activities(title)").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data, None

    @staticmethod
    def view_past_donation_detail(donation_id: int, user_id: int):
        """Entity Logic (Story 32): View specific past donation details"""
        res = supabase.table("donations").select("*, activities(title, description, status)").eq("donation_id", donation_id).eq("user_id", user_id).execute()
        if not res.data:
            return None, "Donation record not found."
        return res.data[0], None