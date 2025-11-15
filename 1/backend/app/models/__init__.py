from ..main import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

# 已有的User模型...
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关联游戏结果（一个用户可有多条记录）
    game_results = relationship("GameResult", back_populates="user")

# 新增游戏结果模型
class GameResult(Base):
    __tablename__ = "game_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户
    time_seconds = Column(Integer, nullable=False)  # 游戏用时（秒）
    steps = Column(Integer, nullable=False)  # 游戏步数
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # 记录时间
    
    # 反向关联用户
    user = relationship("User", back_populates="game_results")