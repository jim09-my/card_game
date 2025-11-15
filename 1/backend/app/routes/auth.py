from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..main import get_db
from ..schemas import UserCreate, UserResponse, UserLogin, Token
from ..crud import get_user_by_email, get_user_by_username, create_user
from ..auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",  # 路由前缀，最终接口为 /auth/register 和 /auth/login
    tags=["auth"]    # 分组标签（Swagger文档用）
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册接口"""
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # 检查用户名是否已存在
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # 创建新用户
    return create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """用户登录接口（返回JWT令牌）"""
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},  # 令牌中存储用户ID（"sub"为标准字段）
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}