from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 用户响应模型（简化版，无邮箱）
class UserResponse(BaseModel):
    id: int
    username: str
    points: int = 0
    created_at: datetime

# 创建用户模型（简化版，无邮箱）
class UserCreate(BaseModel):
    username: str
    password: str

# 用户登录模型
class UserLogin(BaseModel):
    username: str
    password: str

# Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# 游戏结果响应模型
class GameResultResponse(BaseModel):
    id: int
    username: str
    game_mode: str
    time_seconds: int
    steps: int
    score: int = 0
    created_at: datetime

# 创建游戏结果模型
class GameResultCreate(BaseModel):
    username: str
    game_mode: str
    time_seconds: int
    steps: int
    score: Optional[int] = 0

# 游戏步骤上传模型
class GameStepCreate(BaseModel):
    username: str
    game_mode: str
    step: int
    timestamp: int

# 道具购买请求（简化版）
class BuyItemRequest(BaseModel):
    username: str
    item: str  # "delay" 或 "block"
