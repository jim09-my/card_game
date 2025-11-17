from fastapi import FastAPI
from .routes.auth import router as auth_router
from .routes.game import router as game_router

# 初始化FastAPI应用
app = FastAPI(title="Card Game Backend (Simplified)")

# 注册路由
app.include_router(auth_router, prefix="/auth", tags=["认证"])
app.include_router(game_router, prefix="/game", tags=["游戏"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Card Game Backend API 运行正常"}
