from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    points: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用户更新模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    points: Optional[int] = None

# 游戏结果响应模型
class GameResultResponse(BaseModel):
    id: int
    game_mode: str
    time_seconds: int
    steps: int
    score: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# 游戏最佳记录响应
class UserBestRecords(BaseModel):
    fastest_time: Optional[int] = None
    fastest_time_date: Optional[datetime] = None
    fewest_steps: Optional[int] = None
    fewest_steps_date: Optional[datetime] = None
    total_games: int = 0

# 创建用户模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 创建游戏结果模型
class GameResultCreate(BaseModel):
    game_mode: str
    time_seconds: int
    steps: int
    score: Optional[int] = 0

# 用户登录模型
class UserLogin(BaseModel):
    username: str
    password: str

# Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# 用户完整信息（含游戏历史）
class UserWithHistory(UserResponse):
    game_history: List[GameResultResponse] = []
    
    class Config:
        from_attributes = True

# 道具相关模型
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = ""
    cost: int
    effect: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用户道具关联模型
class UserItemBase(BaseModel):
    user_id: int
    item_id: int
    quantity: int = 1

class UserItemCreate(UserItemBase):
    pass

class UserItemResponse(BaseModel):
    id: int
    user_id: int
    item: ItemResponse  # 嵌套道具信息
    quantity: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用户拥有的所有道具
class UserItemsResponse(BaseModel):
    items: List[UserItemResponse]

# 道具购买请求
class PurchaseItemRequest(BaseModel):
    item_id: int

# 道具使用请求
class UseItemRequest(BaseModel):
    item_name: str