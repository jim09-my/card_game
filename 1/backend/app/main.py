from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Config
from .routes.auth import router as auth_router
from .routes.game import router as game_router  # 导入游戏路由

# 数据库初始化（不变）
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 初始化FastAPI应用
app = FastAPI(title="Card Game Backend")

# 注册路由
app.include_router(auth_router)
app.include_router(game_router)  # 新增游戏相关接口

# 依赖项和健康检查（不变）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}