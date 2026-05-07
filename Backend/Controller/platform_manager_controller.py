# Controller/platform_manager_controller.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta, timezone

from dependencies import get_platform_manager
from Entities.platform_manager_action import (
    PlatformManagerEntity, 
    CategoryCreate, 
    CategoryUpdate,
    PlatformManagerLoginRequest,
    PlatformManagerToken
)

router = APIRouter(prefix="/platform", tags=["Platform Manager Controller (BCE Class Mode)"])

# ============================================================
# --- Controller Classes （Story 33 - 42）---
# ============================================================

class ManagerLoginController:
    def execute(self, login_data: PlatformManagerLoginRequest):
        """Story 38: Login to my account"""
        token_response, error = PlatformManagerEntity.login_manager(login_data)
        if error:
            status_code = 401 if "Incorrect" in error else 403
            raise HTTPException(status_code=status_code, detail=error)
        return token_response

class ManagerLogoutController:
    def execute(self):
        """Story 39: Logout of my account"""
        return {"message": "Successfully logged out. Please discard your token."}

class CreateCategoryController:
    def execute(self, cat_data: CategoryCreate):
        """Story 33: Create fundraising activity category"""
        category, error = PlatformManagerEntity.create_category(cat_data)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return category

class ViewCategoryController:
    def execute(self, category_id: int):
        """Story 34: View fundraising activity category"""
        category, error = PlatformManagerEntity.view_category(category_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return category

class UpdateCategoryController:
    def execute(self, category_id: int, cat_data: CategoryUpdate):
        """Story 35: Update fundraising activity category"""
        category, error = PlatformManagerEntity.update_category(category_id, cat_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return category

class SuspendCategoryController:
    def execute(self, category_id: int):
        """Story 36: Suspend fundraising activity category"""
        result, error = PlatformManagerEntity.suspend_category(category_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return result

class SearchCategoriesController:
    def execute(self, name: Optional[str]):
        """Story 37: Search for fundraising categories"""
        categories, error = PlatformManagerEntity.search_categories(name)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return categories

class GenerateDailyReportController:
    def execute(self):
        """Story 40: Generate a daily report"""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        report_data, error = PlatformManagerEntity.generate_stats_by_date(start_of_day, now)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {"report_type": "Daily", "data": report_data}

class GenerateWeeklyReportController:
    def execute(self):
        """Story 41: Generate a weekly report"""
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=7)
        report_data, error = PlatformManagerEntity.generate_stats_by_date(start_of_week, now)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {"report_type": "Weekly", "data": report_data}

class GenerateMonthlyReportController:
    def execute(self):
        """Story 42: Generate a monthly report"""
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        report_data, error = PlatformManagerEntity.generate_stats_by_date(start_of_month, now)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {"report_type": "Monthly", "data": report_data}


# ============================================================
#  Route binding: Instantiate these classes and call execute()
# ============================================================

@router.post("/login", response_model=PlatformManagerToken)
def route_manager_login(login_data: PlatformManagerLoginRequest):
    return ManagerLoginController().execute(login_data)

@router.post("/logout")
def route_manager_logout(pm_user=Depends(get_platform_manager)):
    return ManagerLogoutController().execute()

@router.post("/categories")
def route_create_category(cat_data: CategoryCreate, pm_user=Depends(get_platform_manager)):
    return CreateCategoryController().execute(cat_data)

@router.get("/categories/{category_id}")
def route_view_category(category_id: int, pm_user=Depends(get_platform_manager)):
    return ViewCategoryController().execute(category_id)

@router.patch("/categories/{category_id}")
def route_update_category(category_id: int, cat_data: CategoryUpdate, pm_user=Depends(get_platform_manager)):
    return UpdateCategoryController().execute(category_id, cat_data)

@router.post("/categories/{category_id}/suspend")
def route_suspend_category(category_id: int, pm_user=Depends(get_platform_manager)):
    return SuspendCategoryController().execute(category_id)

@router.get("/categories")
def route_search_categories(name: Optional[str] = Query(None), pm_user=Depends(get_platform_manager)):
    return SearchCategoriesController().execute(name)

@router.get("/reports/daily")
def route_generate_daily_report(pm_user=Depends(get_platform_manager)):
    return GenerateDailyReportController().execute()

@router.get("/reports/weekly")
def route_generate_weekly_report(pm_user=Depends(get_platform_manager)):
    return GenerateWeeklyReportController().execute()

@router.get("/reports/monthly")
def route_generate_monthly_report(pm_user=Depends(get_platform_manager)):
    return GenerateMonthlyReportController().execute()