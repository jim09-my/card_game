from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from .. import schemas, simple_storage
from ..auth import (
    get_current_user,
    create_access_token,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate):
    """用户注册接口（简化版，无邮箱）"""
    # 检查用户数量限制
    if len(simple_storage.users) >= simple_storage.MAX_USERS:
        raise HTTPException(
            status_code=400,
            detail=f"用户数量已达上限（最多{simple_storage.MAX_USERS}人）"
        )
    
    # 检查用户名是否已存在
    if simple_storage.get_user_by_username(user.username):
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    # 创建新用户
    new_user = simple_storage.create_user(user.username, user.password)
    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="注册失败"
        )
    
    # 返回用户数据（排除敏感信息）
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "points": new_user["points"],
        "created_at": new_user["created_at"]
    }

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin):
    """用户登录"""
    # 验证用户凭据
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
