from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Config

# 创建数据库引擎 - 为SQLite配置连接池
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},  # SQLite特定配置
    poolclass=None  # 禁用连接池，避免SQLite线程安全问题
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 数据库依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库表
def init_db():
    from .models import User, GameResult, Item, UserItem
    Base.metadata.create_all(bind=engine)
    
    # 创建一些初始道具
    db = SessionLocal()
    try:
        # 检查是否已有道具数据
        items_count = db.query(Item).count()
        if items_count == 0:
            initial_items = [
                {
                    "name": "增时器",
                    "description": "为困难模式增加60秒时间",
                    "cost": 15,
                    "effect": "time_extension"
                },
                {
                    "name": "翻牌器",
                    "description": "直接翻开一张卡片，无需配对",
                    "cost": 10,
                    "effect": "instant_flip"
                },
                {
                    "name": "提示器",
                    "description": "高亮显示一对匹配的卡片",
                    "cost": 12,
                    "effect": "hint"
                },
                {
                    "name": "连击加成",
                    "description": "下一次匹配获得双倍积分",
                    "cost": 20,
                    "effect": "double_score"
                }
            ]
            
            for item_data in initial_items:
                item = Item(**item_data)
                db.add(item)
            
            db.commit()
            print("已创建初始道具数据")
    finally:
        db.close()