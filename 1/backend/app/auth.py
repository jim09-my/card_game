from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from . import simple_storage

# JWT 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 安全方案
security = HTTPBearer()

# JWT Token 创建
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 验证用户
def authenticate_user(username: str, password: str):
    """验证用户凭据"""
    return simple_storage.authenticate_user(username, password)

# 获取当前用户
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """依赖函数：验证 JWT token 并返回当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解析 JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
    except jwt.PyJWTError:
        raise credentials_exception
    
    # 从内存存储获取用户
    user = simple_storage.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    # 返回用户数据（排除敏感信息）
    return {
        "id": user["id"],
        "username": user["username"],
        "points": user["points"],
        "created_at": user["created_at"]
    }
