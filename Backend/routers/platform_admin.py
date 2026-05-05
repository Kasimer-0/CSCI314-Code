from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import Optional
from datetime import datetime, timedelta, timezone

import schemas
from database import supabase
from dependencies import get_current_admin # Use existing Admin authentication

router = APIRouter(prefix="/platform", tags=["Sprint 3 - Platform Management"])

# ================= Categories Management (Story 33-36) =================
@router.get("/categories")
def get_all_categories(current_admin: dict = Depends(get_current_admin)):
    return supabase.table("categories").select("*").order("category_id").execute().data

@router.post("/categories")
def create_category(cat: schemas.CategoryCreate, current_admin: dict = Depends(get_current_admin)):
    new_cat = {"name": cat.name, "description": cat.description, "created_at": datetime.now(timezone.utc).isoformat()}
    return supabase.table("categories").insert(new_cat).execute().data[0]

@router.patch("/categories/{category_id}")
def update_category(category_id: int, cat: schemas.CategoryUpdate, current_admin: dict = Depends(get_current_admin)):
    update_data = cat.dict(exclude_unset=True)
    if not update_data: raise HTTPException(status_code=400, detail="No data")
    res = supabase.table("categories").update(update_data).eq("category_id", category_id).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Category not found")
    return res.data[0]

@router.post("/categories/{category_id}/toggle-archive")
def toggle_archive_category(category_id: int, current_admin: dict = Depends(get_current_admin)):
    cat = supabase.table("categories").select("is_archived").eq("category_id", category_id).execute()
    if not cat.data: raise HTTPException(status_code=404, detail="Category not found")
    new_status = not cat.data[0]["is_archived"]
    res = supabase.table("categories").update({"is_archived": new_status}).eq("category_id", category_id).execute()
    return {"message": f"Category archived status set to {new_status}"}

# ================= General Settings (Story 37) =================
@router.get("/settings")
def get_settings(current_admin: dict = Depends(get_current_admin)):
    return supabase.table("site_settings").select("*").execute().data

@router.put("/settings/{setting_key}")
def update_setting(setting_key: str, setting: schemas.SiteSettingUpdate, current_admin: dict = Depends(get_current_admin)):
    res = supabase.table("site_settings").update({"setting_value": setting.setting_value, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("setting_key", setting_key).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Setting key not found")
    return res.data[0]

# ================= Reporting & Export (Story 38-41) =================
def generate_stats_by_date(start_date: datetime, end_date: datetime):
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()
    # Statistics on newly registered users
    users_resp = supabase.table("users").select("user_id", count="exact").gte("created_at", start_str).lte("created_at", end_str).execute()
    # Statistics on donation transactions
    donations_resp = supabase.table("donations").select("amount").gte("created_at", start_str).lte("created_at", end_str).execute()
    total_amount = sum(d["amount"] for d in donations_resp.data) if donations_resp.data else 0.0
    
    return {
        "new_users": users_resp.count if users_resp.count else 0,
        "total_donations_amount": total_amount,
        "transactions_count": len(donations_resp.data) if donations_resp.data else 0
    }

@router.get("/reports/daily")
def daily_report(current_admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return generate_stats_by_date(start_of_day, now)

@router.get("/reports/weekly")
def weekly_report(current_admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=7)
    return generate_stats_by_date(start_of_week, now)

@router.get("/reports/monthly")
def monthly_report(current_admin: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return generate_stats_by_date(start_of_month, now)

@router.get("/reports/export-csv", response_class=PlainTextResponse)
def export_donations_csv(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    current_admin: dict = Depends(get_current_admin)
):
    """Story 41: Export custom report to CSV (Excel compatible)"""
    resp = supabase.table("donations").select("*, activities(title)").gte("created_at", f"{start_date}T00:00:00Z").lte("created_at", f"{end_date}T23:59:59Z").execute()
    donations = resp.data
    
    # Build a CSV string
    csv_content = "Donation ID,Activity Title,Amount,Is Anonymous,Date\n"
    for d in donations:
        activity_title = d.get("activities", {}).get("title", "Unknown").replace(",", " ") # Prevent comma from breaking CSV format
        csv_content += f"{d['donation_id']},{activity_title},{d['amount']},{d['is_anonymous']},{d['created_at']}\n"
        
    return PlainTextResponse(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=report_{start_date}_to_{end_date}.csv"})