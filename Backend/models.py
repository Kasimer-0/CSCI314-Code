# models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

# ==========================================
# 1. User Account Entity (Story #6 - #10)
# Responsibilities: Only responsible for security, login credentials, and account ban status.
# ==========================================
class UserAccount(Base):
    __tablename__ = "user_accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(String, default="Pending") # Pending, Active, Suspended
    is_suspended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("UserProfile", back_populates="account", uselist=False, cascade="all, delete-orphan")

# ==========================================
# 2. User Profile Entity (Story #1 - #5)
# Responsibilities: Only responsible for personal public information and role assignment
# ==========================================
class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    # Foreign key linking to the user_accounts table, ensuring each Account has only one Profile
    account_id = Column(Integer, ForeignKey("user_accounts.account_id"), unique=True, nullable=False)
    
    username = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    role_id = Column(Integer, nullable=False) # 1: Donee, 2: Fundraiser, 3: Platform Manager, 0: User Admin
    
    account = relationship("UserAccount", back_populates="profile")

    activities = relationship("Activity", back_populates="fundraiser_profile")
    donations = relationship("Donation", back_populates="donee_profile")
    bookmarks = relationship("Bookmark", back_populates="donee_profile")

# ==========================================
# 3. Category Entity (Story #33 - #37)
# ==========================================
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    activities = relationship("Activity", back_populates="category")

# ==========================================
# 4. Activity Entity (Story #13 - #23)
# ==========================================
class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    fundraiser_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    is_private = Column(Boolean, default=False)
    status = Column(String, default="Ongoing")
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    category = relationship("Category", back_populates="activities")
    fundraiser_profile = relationship("UserProfile", back_populates="activities")
    donations = relationship("Donation", back_populates="activity")
    bookmarks = relationship("Bookmark", back_populates="activity")

# ==========================================
# 5. Donation Entity (Story #31 - #32)
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
# 6. Bookmark Entity (Story #26 - #28)
# ==========================================
class Bookmark(Base):
    __tablename__ = "bookmarks"

    bookmark_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.activity_id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    donee_profile = relationship("UserProfile", back_populates="bookmarks")
    activity = relationship("Activity", back_populates="bookmarks")