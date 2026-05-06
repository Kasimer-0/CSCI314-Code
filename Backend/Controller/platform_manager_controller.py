# Control/platform_manager_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta, timezone

# 引入平台经理鉴权依赖
from dependencies import get_platform_manager

# 引入刚刚创建好的 Platform Manager 专属 Entity 和 Schema
from Entities.platform_manager_action import (
    PlatformManagerEntity, 
    CategoryCreate, 
    CategoryUpdate,
    PlatformManagerLoginRequest,
    PlatformManagerToken
)

router = APIRouter(prefix="/platform", tags=["Platform Manager Controller"])

# ==========================================
# --- Auth (Story 38, 39) ---
# ==========================================
@router.post("/login", response_model=PlatformManagerToken)
def manager_login(login_data: PlatformManagerLoginRequest):
    """Story 38: Login to my account (Platform Manager Exclusive)"""
    token_response, error = PlatformManagerEntity.login_manager(login_data)
    if error:
        status_code = 401 if "Incorrect" in error else 403
        raise HTTPException(status_code=status_code, detail=error)
    return token_response

@router.post("/logout")
def manager_logout():
    """Story 39: Logout of my account (Platform Manager Exclusive)"""
    return {"message": "Successfully logged out. Please discard your token."}


# ==========================================
# --- Category Management (Story 33 - 37) ---
# ==========================================
@router.post("/categories")
def create_category(cat_data: CategoryCreate, pm: dict = Depends(get_platform_manager)):
    """Story 33: Create fundraising activity category"""
    category, error = PlatformManagerEntity.create_category(cat_data)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return category

@router.get("/categories/{category_id}")
def view_category(category_id: int, pm: dict = Depends(get_platform_manager)):
    """Story 34: View fundraising activity category"""
    category, error = PlatformManagerEntity.view_category(category_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return category

@router.patch("/categories/{category_id}")
def update_category(category_id: int, cat_data: CategoryUpdate, pm: dict = Depends(get_platform_manager)):
    """Story 35: Update fundraising activity category"""
    category, error = PlatformManagerEntity.update_category(category_id, cat_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return category

@router.post("/categories/{category_id}/suspend")
def suspend_category(category_id: int, pm: dict = Depends(get_platform_manager)):
    """Story 36: Suspend fundraising activity category"""
    result, error = PlatformManagerEntity.suspend_category(category_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/categories")
def search_categories(name: Optional[str] = Query(None, description="Search by category name"), pm: dict = Depends(get_platform_manager)):
    """Story 37: Search for fundraising categories"""
    categories, error = PlatformManagerEntity.search_categories(name)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return categories


# ==========================================
# --- Reporting (Story 40 - 42) ---
# ==========================================
@router.get("/reports/daily")
def generate_daily_report(pm: dict = Depends(get_platform_manager)):
    """Story 40: Generate a daily report"""
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    report_data, error = PlatformManagerEntity.generate_stats_by_date(start_of_day, now)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"report_type": "Daily", "data": report_data}

@router.get("/reports/weekly")
def generate_weekly_report(pm: dict = Depends(get_platform_manager)):
    """Story 41: Generate a weekly report"""
    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=7)
    
    report_data, error = PlatformManagerEntity.generate_stats_by_date(start_of_week, now)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"report_type": "Weekly", "data": report_data}

@router.get("/reports/monthly")
def generate_monthly_report(pm: dict = Depends(get_platform_manager)):
    """Story 42: Generate a monthly report"""
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    report_data, error = PlatformManagerEntity.generate_stats_by_date(start_of_month, now)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"report_type": "Monthly", "data": report_data}