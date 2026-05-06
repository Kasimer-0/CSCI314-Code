from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from Entities.user_account import UserAccountEntity

security = HTTPBearer()
SECRET_KEY = "CSIT314_2026_SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION_!@#$"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ⚠️ 调用 Entity 的方法去查数据库，而不是在这里直接写 supabase
    user = UserAccountEntity.get_user_by_email_for_auth(email)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ================= 角色鉴权 (无需修改) =================
def get_user_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_id") != 0: raise HTTPException(status_code=403, detail="User Admin access required")
    return current_user

def get_donee(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_id") != 1: raise HTTPException(status_code=403, detail="Donee access required")
    return current_user

def get_fundraiser(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_id") != 2: raise HTTPException(status_code=403, detail="Fundraiser access required")
    return current_user

def get_platform_manager(current_user: dict = Depends(get_current_user)):
    if current_user.get("role_id") != 3: raise HTTPException(status_code=403, detail="Platform Manager access required")
    return current_user