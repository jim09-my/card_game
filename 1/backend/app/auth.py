from datetime import datetime, timedelta
from typing import Optional, Annotated
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # 用于提取令牌

# 已有的导入和配置...
from .main import get_db
from .crud import get_user_by_email, pwd_context, get_user_by_id  # 替换原有导入
from .schemas import TokenData
from .config import Config

# 定义令牌提取器（从请求头Authorization: Bearer <token>中提取）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 新增：验证令牌并获取当前用户
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    """依赖项：验证令牌并返回当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # 从令牌中获取用户ID（"sub"是我们存储的键）
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    
    # 查询用户是否存在
    user = get_user_by_username(db, username=None)  # 先用占位，实际用ID查询
    # 修正：通过ID查询用户（需在crud.py中新增get_user_by_id函数）
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user