from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta, timezone

# Import role permissions and check dependencies
from dependencies import get_platform_manager

# Import the newly split Entities
from Entities.platform_category import CategoryEntity, CategoryCreate, CategoryUpdate
from Entities.platform_report import PlatformReportEntity
from Entities.user_account import UserAccountEntity # Used to manage login/logout logic
router = APIRouter(prefix="/platform", tags=["Platform Manager Controller (BCE Class Mode)"])

# ============================================================
# --- 1. Authentication related Controllers (Story 38 - 39) ---
# ============================================================

class ManagerLoginController:
    def execute(self, login_data):
        """Story 38: Login to platform manager account"""
        # Call the login logic in UserAccountEntity specifically designed for Manager
        token_response, error = UserAccountEntity.login_manager(login_data)
        if error:
            status_code = 401 if "Incorrect" in error else 403
            raise HTTPException(status_code=status_code, detail=error)
        return token_response

class ManagerLogoutController:
    def execute(self):
        """Story 39: Logout of my account"""
        response, error = UserAccountEntity.logout_manager()
        if error:
            raise HTTPException(status_code=500, detail=error)
        return response


# ============================================================
# --- 2. Category Management related Controllers (Story 33 - 37) ---
# ============================================================

class CreateCategoryController:
    def execute(self, cat_data: CategoryCreate):
        """Story 33: Create fundraising activity category"""
        category, error = CategoryEntity.create_category(cat_data)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return category

class ViewCategoryController:
    def execute(self, category_id: int):
        """Story 34: View fundraising activity category"""
        category, error = CategoryEntity.get_category(category_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return category

class UpdateCategoryController:
    def execute(self, category_id: int, cat_data: CategoryUpdate):
        """Story 35: Update fundraising activity category"""
        category, error = CategoryEntity.update_category(category_id, cat_data)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return category

class SuspendCategoryController:
    def execute(self, category_id: int):
        """Story 36: Suspend fundraising activity category"""
        success, error = CategoryEntity.suspend_category(category_id)
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"message": "Category suspended successfully."}

class SearchCategoriesController:
    def execute(self, name: Optional[str]):
        """Story 37: Search for fundraising categories"""
        categories, error = CategoryEntity.search_categories(name)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return categories


# ============================================================
# --- 3. Data Reports Controllers (Story 40 - 42) ---
# ============================================================

class GenerateDailyReportController:
    def execute(self):
        """Story 40: Generate a daily report"""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        report, error = PlatformReportEntity.generate_stats(start_of_day, now)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {"report_type": "Daily", "data": report}

class GenerateWeeklyReportController:
    def execute(self):
        """Story 41: Generate a weekly report"""
        now = datetime.now(timezone.utc)
        start_of_week = now - timedelta(days=7)
        report, error = PlatformReportEntity.generate_stats(start_of_week, now)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {"report_type": "Weekly", "data": report}

class GenerateMonthlyReportController:
    def execute(self):
        """Story 42: Generate a monthly report"""
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        report, error = PlatformReportEntity.generate_stats(start_of_month, now)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {"report_type": "Monthly", "data": report}


# ============================================================
# Route Binding: Instantiate Classes and Execute
# ============================================================

@router.post("/login")
def route_manager_login(login_data: dict): # Receive raw JSON for login
    """API for Story 38"""
    return ManagerLoginController().execute(login_data)

@router.post("/logout")
def route_manager_logout(pm_user=Depends(get_platform_manager)):
    """API for Story 39"""
    return ManagerLogoutController().execute()

@router.post("/categories")
def route_create_category(cat_data: CategoryCreate, pm_user=Depends(get_platform_manager)):
    """API for Story 30"""
    return CreateCategoryController().execute(cat_data)

@router.get("/categories/{category_id}")
def route_view_category(category_id: int, pm_user=Depends(get_platform_manager)):
    """API for Story 31"""
    return ViewCategoryController().execute(category_id)

@router.patch("/categories/{category_id}")
def route_update_category(category_id: int, cat_data: CategoryUpdate, pm_user=Depends(get_platform_manager)):
    """API for Story 32"""
    return UpdateCategoryController().execute(category_id, cat_data)

@router.post("/categories/{category_id}/suspend")
def route_suspend_category(category_id: int, pm_user=Depends(get_platform_manager)):
    """API for Story 33"""
    return SuspendCategoryController().execute(category_id)

@router.get("/categories")
def route_search_categories(name: Optional[str] = Query(None), pm_user=Depends(get_platform_manager)):
    """API for Story 34"""
    return SearchCategoriesController().execute(name)

@router.get("/reports/daily")
def route_generate_daily_report(pm_user=Depends(get_platform_manager)):
    """API for Story 40"""
    return GenerateDailyReportController().execute()

@router.get("/reports/weekly")
def route_generate_weekly_report(pm_user=Depends(get_platform_manager)):
    """API for Story 41"""
    return GenerateWeeklyReportController().execute()

@router.get("/reports/monthly")
def route_generate_monthly_report(pm_user=Depends(get_platform_manager)):
    """API for Story 42"""
    return GenerateMonthlyReportController().execute()
