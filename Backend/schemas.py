from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    phone_number: Optional[str] = None
    role_id: int = 1  # 1: Donor/Donee, 2: Organization/Fundraiser, 0: Admin

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    role_id: int
    status: str
    phone_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 新增模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None