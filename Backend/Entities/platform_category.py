from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from models import Category
from dependencies import get_db

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryEntity:
    @staticmethod
    def create_category(cat_data: CategoryCreate):
        """Business Logic: Create a fundraising campaign category. (Story 33)"""
        db: Session = next(get_db())
        try:
            new_cat = Category(name=cat_data.name, description=cat_data.description)
            db.add(new_cat)
            db.commit()
            db.refresh(new_cat)
            return new_cat, None
        finally:
            db.close()

    @staticmethod
    def get_category(category_id: int):
        """Business Logic: Retrieve a fundraising campaign category by ID. (Story 34)"""
        db: Session = next(get_db())
        try:
            category = db.query(Category).filter(Category.category_id == category_id).first()
            return category, None if category else ("Category not found.", None)
        finally:
            db.close()

    @staticmethod
    def update_category(category_id: int, cat_data: CategoryUpdate):
        """Business Logic: Update a fundraising campaign category. (Story 35)"""
        db: Session = next(get_db())
        try:
            category = db.query(Category).filter(Category.category_id == category_id).first()
            if not category: return None, "Category not found."
            if cat_data.name: category.name = cat_data.name
            if cat_data.description: category.description = cat_data.description
            db.commit()
            db.refresh(category)
            return category, None
        finally:
            db.close()

    @staticmethod
    def suspend_category(category_id: int):
        """Business Logic: Suspend a fundraising campaign category. (Story 36)"""
        db: Session = next(get_db())
        try:
            category = db.query(Category).filter(Category.category_id == category_id).first()
            if not category: return None, "Category not found."
            category.is_archived = True
            db.commit()
            return True, None
        finally:
            db.close()

    @staticmethod
    def search_categories(name_query: Optional[str]):
        """Business Logic: Search for fundraising campaign categories. (Story 37)"""
        db: Session = next(get_db())
        try:
            query = db.query(Category)
            if name_query:
                query = query.filter(Category.name.ilike(f"%{name_query}%"))
            return query.all(), None
        finally:
            db.close()