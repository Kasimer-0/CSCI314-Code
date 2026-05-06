# Entities/platform_manager_action.py

from pydantic import BaseModel, EmailStr
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
class PlatformManagerLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PlatformManagerToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ==========================================
# 2. Entity Class (Business Logic & Database)
# ==========================================
class PlatformManagerEntity:

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """Helper for Story 38"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False

    @staticmethod
    def login_manager(login_data: PlatformManagerLoginRequest):
        """Entity Logic (Story 38): Authenticate Platform Manager and generate token"""
        response = supabase.table("users").select("*").eq("email", login_data.email).execute()
        user = response.data[0] if response.data else None

        if not user or not PlatformManagerEntity.verify_password(login_data.password, user.get("password_hash")):
            return None, "Incorrect email or password."
        
        # 确保只有 Platform Manager (假设 role_id = 3) 能够走这个专属通道
        if user.get("role_id") != 3:
            return None, "Access denied. Only Platform Managers can log in here."
            
        if user.get("status") == "Suspended":
            return None, "This account has been suspended."

        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user["email"], "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"access_token": token, "token_type": "bearer"}, None

    @staticmethod
    def create_category(cat_data: CategoryCreate):
        """Entity Logic (Story 33): Create fundraising activity category"""
        new_cat = {
            "name": cat_data.name, 
            "description": cat_data.description, 
            "is_archived": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        res = supabase.table("categories").insert(new_cat).execute()
        if not res.data:
            return None, "Failed to create category."
        return res.data[0], None

    @staticmethod
    def view_category(category_id: int):
        """Entity Logic (Story 34): View fundraising activity category"""
        res = supabase.table("categories").select("*").eq("category_id", category_id).execute()
        if not res.data:
            return None, "Category not found."
        return res.data[0], None

    @staticmethod
    def update_category(category_id: int, cat_data: CategoryUpdate):
        """Entity Logic (Story 35): Update fundraising activity category"""
        update_data = cat_data.dict(exclude_unset=True)
        if not update_data:
            return None, "No data provided for update."
            
        res = supabase.table("categories").update(update_data).eq("category_id", category_id).execute()
        if not res.data:
            return None, "Failed to update category or category not found."
        return res.data[0], None

    @staticmethod
    def suspend_category(category_id: int):
        """Entity Logic (Story 36): Suspend fundraising activity category"""
        # Suspend by marking it as archived
        res = supabase.table("categories").update({"is_archived": True}).eq("category_id", category_id).execute()
        if not res.data:
            return None, "Failed to suspend category."
        return {"message": f"Category {category_id} suspended successfully."}, None

    @staticmethod
    def search_categories(name_query: Optional[str]):
        """Entity Logic (Story 37): Search for fundraising categories"""
        query = supabase.table("categories").select("*")
        if name_query:
            query = query.ilike("name", f"%{name_query}%")
        res = query.execute()
        return res.data, None

    @staticmethod
    def generate_stats_by_date(start_date: datetime, end_date: datetime):
        """Helper Logic for Story 40, 41, 42: Aggregate platform statistics"""
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        # 统计新活动数量
        activities_resp = supabase.table("activities").select("activity_id", count="exact").gte("created_at", start_str).lte("created_at", end_str).execute()
        
        # 统计捐款流水
        donations_resp = supabase.table("donations").select("amount").gte("created_at", start_str).lte("created_at", end_str).execute()
        total_amount = sum(d["amount"] for d in donations_resp.data) if donations_resp.data else 0.0
        
        return {
            "period_start": start_str,
            "period_end": end_str,
            "new_activities_launched": activities_resp.count if activities_resp.count else 0,
            "total_donations_amount": total_amount,
            "transactions_count": len(donations_resp.data) if donations_resp.data else 0
        }, None