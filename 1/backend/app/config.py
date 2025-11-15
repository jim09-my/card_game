import os
from dotenv import load_dotenv

# 加载环境变量（从 .env 文件）
load_dotenv()

class Config:
    # 数据库配置（根据选择的数据库修改）
    # PostgreSQL 示例
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/card_game_db"
    )
    # MySQL 示例（需替换为 pymysql 驱动）
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #     "DATABASE_URL",
    #     "mysql+pymysql://user:password@localhost:3306/card_game_db"
    # )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用 SQLAlchemy 跟踪修改（优化性能）