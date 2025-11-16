from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import datetime

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)  # 用户积分
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关联游戏结果（一个用户可有多条记录）
    game_results = relationship("GameResult", back_populates="user")
    # 关联用户道具
    user_items = relationship("UserItem", back_populates="user")

# 游戏结果模型
class GameResult(Base):
    __tablename__ = "game_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_mode = Column(String(20), nullable=False)  # 'simple' 或 'hard'
    time_seconds = Column(Integer, nullable=False)  # 游戏用时（秒）
    steps = Column(Integer, nullable=False)  # 游戏步数
    score = Column(Integer, default=0)  # 游戏得分
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 反向关联用户
    user = relationship("User", back_populates="game_results")

# 道具定义模型
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # 道具名称
    description = Column(Text)  # 道具描述
    cost = Column(Integer, nullable=False)  # 兑换所需积分
    effect = Column(String(20), nullable=False)  # 效果类型：'time_extension', 'instant_flip'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关联用户道具
    user_items = relationship("UserItem", back_populates="item")

# 用户道具关联模型
class UserItem(Base):
    __tablename__ = "user_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)  # 道具数量
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 反向关联
    user = relationship("User", back_populates="user_items")
    item = relationship("Item", back_populates="user_items")