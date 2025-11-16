from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Config
from .routes.auth import router as auth_router
from .routes.game import router as game_router  # 导入游戏路由
from .database import init_db  # 导入数据库初始化函数

# 数据库初始化
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 初始化FastAPI应用
app = FastAPI(title="Card Game Backend")

# 注册路由
app.include_router(auth_router, prefix="/auth", tags=["认证"])
app.include_router(game_router, prefix="/game", tags=["游戏"])

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库和初始数据"""
    init_db()
    print("数据库初始化完成")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected", "message": "Card Game Backend API 运行正常"}