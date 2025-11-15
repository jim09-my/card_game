from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# 已有的模型...
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    class Config:
        orm_mode = True

# 新增游戏结果相关模型
class GameResultCreate(BaseModel):
    time_seconds: int  # 游戏用时（秒）
    steps: int         # 游戏步数

class GameResultResponse(BaseModel):
    id: int
    user_id: int
    time_seconds: int
    steps: int
    created_at: datetime
    class Config:
        orm_mode = True

# 带用户信息的游戏结果（可选）
class GameResultWithUser(GameResultResponse):
    user: UserResponse