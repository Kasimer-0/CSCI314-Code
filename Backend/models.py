# models.py 最终终结版 - 修复 ImportError 和所有关联关系

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

# ==========================================
# 1. User Account Entity
# ==========================================
class UserAccount(Base):
    __tablename__ = "user_accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(String, default="Pending")
    is_suspended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("UserProfile", back_populates="account", uselist=False, cascade="all, delete-orphan")

# ==========================================
# 2. User Profile Entity
# ==========================================
class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("user_accounts.account_id"))
    username = Column(String)
    phone_number = Column(String, nullable=True)
    role_id = Column(Integer)
    status = Column(String, default="Active")
    is_suspended = Column(Boolean, default=False)

    account = relationship("UserAccount", back_populates="profile")
    bookmarks = relationship("Bookmark", back_populates="user_profile")
    donations = relationship("Donation", back_populates="donee_profile")
    activities = relationship("Activity", back_populates="creator")

# ==========================================
# 3. Category Entity (修复 ImportError 的关键)
# ==========================================
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # 与 Activity 的关联
    activities = relationship("Activity", back_populates="category")

# ==========================================
# 4. Activity Entity
# ==========================================
class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    # 修复：添加 category_id 外键
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(String)
    goal_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    creator = relationship("UserProfile", back_populates="activities")
    bookmarks = relationship("Bookmark", back_populates="activity")
    donations = relationship("Donation", back_populates="activity")
    # 修复：与 Category 的握手
    category = relationship("Category", back_populates="activities")

# ==========================================
# 5. Donation Entity
# ==========================================
class Donation(Base):
    __tablename__ = "donations"

    donation_id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.activity_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    amount = Column(Float, nullable=False)
    message = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    donee_profile = relationship("UserProfile", back_populates="donations")
    activity = relationship("Activity", back_populates="donations")

# ==========================================
# 6. Bookmark Entity
# ==========================================
class Bookmark(Base):
    __tablename__ = "bookmarks"

    bookmark_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.activity_id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_profile = relationship("UserProfile", back_populates="bookmarks")
    activity = relationship("Activity", back_populates="bookmarks")