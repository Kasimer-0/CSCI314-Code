# Controller/platform_manager_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone

from dependencies import get_db, get_platform_manager
from Entities.platform_manager_action import (
    PlatformManagerEntity, 
    CategoryCreate, 
    CategoryUpdate,
    PlatformManagerLoginRequest,
    PlatformManagerToken
)

router = APIRouter(prefix="/platform", tags=["Platform Manager Controller"])

@router.post("/login", response_model=PlatformManagerToken)
def manager_login(login_data: PlatformManagerLoginRequest, db: Session = Depends(get_db)):
    """Story 38: Login to my account"""
    token_response, error = PlatformManagerEntity.login_manager(db, login_data)
    if error:
        status_code = 401 if "Incorrect" in error else 403
        raise HTTPException(status_code=status_code, detail=error)
    return token_response

@router.post("/logout")
def manager_logout(pm_user = Depends(get_platform_manager)):
    """Story 39: Logout of my account"""
    return {"message": "Successfully logged out. Please discard your token."}

@router.post("/categories")
def create_category(cat_data: CategoryCreate, db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 33: Create fundraising activity category"""
    category, error = PlatformManagerEntity.create_category(db, cat_data)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return category

@router.get("/categories/{category_id}")
def view_category(category_id: int, db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 34: View fundraising activity category"""
    category, error = PlatformManagerEntity.view_category(db, category_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return category

@router.patch("/categories/{category_id}")
def update_category(category_id: int, cat_data: CategoryUpdate, db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 35: Update fundraising activity category"""
    category, error = PlatformManagerEntity.update_category(db, category_id, cat_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return category

@router.post("/categories/{category_id}/suspend")
def suspend_category(category_id: int, db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 36: Suspend fundraising activity category"""
    result, error = PlatformManagerEntity.suspend_category(db, category_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

@router.get("/categories")
def search_categories(name: Optional[str] = Query(None), db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 37: Search for fundraising categories"""
    categories, error = PlatformManagerEntity.search_categories(db, name)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return categories

@router.get("/reports/daily")
def generate_daily_report(db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 40: Generate a daily report"""
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    report_data, error = PlatformManagerEntity.generate_stats_by_date(db, start_of_day, now)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"report_type": "Daily", "data": report_data}

@router.get("/reports/weekly")
def generate_weekly_report(db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 41: Generate a weekly report"""
    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=7)
    report_data, error = PlatformManagerEntity.generate_stats_by_date(db, start_of_week, now)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"report_type": "Weekly", "data": report_data}

@router.get("/reports/monthly")
def generate_monthly_report(db: Session = Depends(get_db), pm_user = Depends(get_platform_manager)):
    """Story 42: Generate a monthly report"""
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    report_data, error = PlatformManagerEntity.generate_stats_by_date(db, start_of_month, now)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return {"report_type": "Monthly", "data": report_data}