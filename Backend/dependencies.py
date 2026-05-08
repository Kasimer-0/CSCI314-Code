from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from database import SessionLocal
from models import UserAccount, UserProfile # Import your models

security = HTTPBearer()

# Keep your original JWT configuration unchanged
SECRET_KEY = "CSIT314_2026_SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION_!@#$"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================================
# DataBase Session dependency
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# Update：Get current user's authentication logic
# ==========================================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Query user data using SQLAlchemy
    account = db.query(UserAccount).filter(UserAccount.email == email).first()
    
    if not account:
        raise HTTPException(status_code=401, detail="User account not found")
    if account.status == "Suspended" or account.is_suspended:
        raise HTTPException(status_code=403, detail="Your account has been suspended")
        
    return account

# ================= Role-Based Access Control =================
def get_user_admin(current_user: UserAccount = Depends(get_current_user)):
    # Add explicit check for the existence of the profile
    if not current_user.profile:
        raise HTTPException(status_code=403, detail="User profile not found")
    if current_user.profile.role_id != 0: 
        raise HTTPException(status_code=403, detail="User Admin access required")
    return current_user

def get_donee(current_user: UserAccount = Depends(get_current_user)):
    if not current_user.profile or current_user.profile.role_id != 1: 
        raise HTTPException(status_code=403, detail="Donee access required")
    return current_user

def get_fundraiser(current_user: UserAccount = Depends(get_current_user)):
    if not current_user.profile or current_user.profile.role_id != 2: 
        raise HTTPException(status_code=403, detail="Fundraiser access required")
    return current_user

def get_platform_manager(current_user: UserAccount = Depends(get_current_user)):
    if not current_user.profile or current_user.profile.role_id != 3: 
        raise HTTPException(status_code=403, detail="Platform Manager access required")
    return current_user