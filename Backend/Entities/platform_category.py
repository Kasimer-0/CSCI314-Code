from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel
from typing import Optional
from database import Base, get_db

# ==========================================
# 1. Pydantic Models (Data Validation)
# ==========================================
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ==========================================
# 2. BCE Entity: Category
# ==========================================
class Category(Base):
    __tablename__ = "categories"

    # --- State: Database table field ---
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False) 

    # Relationship: One category can have multiple fundraising activities
    activities = relationship("Activity", back_populates="category")

    # --- Behavior: Business logic methods ---
    @classmethod
    def create_category(cls, cat_data: CategoryCreate):
        """Business Logic: Create a fundraising campaign category. (Story 33)"""
        db: Session = next(get_db())
        try:
            new_cat = cls(name=cat_data.name, description=cat_data.description)
            db.add(new_cat)
            db.commit()
            db.refresh(new_cat)
            return new_cat, None
        finally:
            db.close()

    @classmethod
    def get_category(cls, category_id: int):
        """Business Logic: Retrieve a fundraising campaign category by ID. (Story 34)"""
        db: Session = next(get_db())
        try:
            category = db.query(cls).filter(cls.category_id == category_id).first()
            return category, None if category else ("Category not found.", None)
        finally:
            db.close()

    @classmethod
    def update_category(cls, category_id: int, cat_data: CategoryUpdate):
        """Business Logic: Update a fundraising campaign category. (Story 35)"""
        db: Session = next(get_db())
        try:
            category = db.query(cls).filter(cls.category_id == category_id).first()
            if not category: return None, "Category not found."
            if cat_data.name: category.name = cat_data.name
            if cat_data.description: category.description = cat_data.description
            db.commit()
            db.refresh(category)
            return category, None
        finally:
            db.close()

    @classmethod
    def suspend_category(cls, category_id: int):
        """Business Logic: Suspend a fundraising campaign category. (Story 36)"""
        db: Session = next(get_db())
        try:
            category = db.query(cls).filter(cls.category_id == category_id).first()
            if not category: return None, "Category not found."
            category.is_archived = True
            db.commit()
            return True, None
        finally:
            db.close()

    @classmethod
    def search_categories(cls, name_query: Optional[str]):
        """Business Logic: Search for fundraising campaign categories. (Story 37)"""
        db: Session = next(get_db())
        try:
            query = db.query(cls)
            if name_query:
                query = query.filter(cls.name.ilike(f"%{name_query}%"))
            return query.all(), None
        finally:
            db.close()