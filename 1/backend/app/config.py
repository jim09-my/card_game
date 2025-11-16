import os
from dotenv import load_dotenv

# 加载环境变量（从 .env 文件）
load_dotenv()

class Config:
    # 数据库配置（使用SQLite用于开发测试）
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./card_game.db"
    )
    # PostgreSQL 生产环境配置示例
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "DATABASE_URL", 
    #     "postgresql://user:password@localhost:5432/card_game_db"
    # )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用 SQLAlchemy 跟踪修改（优化性能）