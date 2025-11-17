from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from .. import schemas, simple_storage
from ..auth import get_current_user

router = APIRouter(prefix="/game", tags=["game"])

@router.post("/upload_result", response_model=schemas.GameResultResponse)
async def upload_game_result(result: schemas.GameResultCreate):
    """上传游戏结果"""
    # 检查用户是否存在
    user = simple_storage.get_user_by_username(result.username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 创建游戏结果
    db_result = simple_storage.add_game_result(
        username=result.username,
        game_mode=result.game_mode,
        time_seconds=result.time_seconds,
        steps=result.steps,
        score=result.score or 0
    )
    
    # 计算积分（根据游戏时间和步数计算）
    if result.game_mode == "simple":
        points = 10 if (result.time_seconds <= 120 and result.steps <= 50) else 5
    else:  # hard mode
        points = 20 if (result.time_seconds <= 180 and result.steps <= 100) else 10
    
    # 更新用户积分
    simple_storage.update_user_points(result.username, points)
    
    return db_result

@router.post("/upload_step")
async def upload_game_step(step: schemas.GameStepCreate):
    """上传游戏步骤（简化版，只记录）"""
    # 检查用户是否存在
    user = simple_storage.get_user_by_username(step.username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"status": "ok", "message": "步骤已记录"}

@router.get("/history", response_model=List[schemas.GameResultResponse])
async def get_game_history(
    username: str,
    limit: int = 100
):
    """获取用户的游戏历史记录"""
    return simple_storage.get_user_game_history(username, limit)

@router.get("/leaderboard")
async def get_leaderboard(
    game_mode: Optional[str] = None,
    limit: int = 10
):
    """获取全球排行榜（按时间排序）"""
    results = simple_storage.get_leaderboard(game_mode, limit)
    
    # 转换为响应格式
    leaderboard = []
    for result in results:
        leaderboard.append({
            "username": result["username"],
            "time_seconds": result["time_seconds"],
            "steps": result["steps"],
            "game_mode": result["game_mode"],
            "score": result["score"],
            "date": result["created_at"].isoformat() if isinstance(result["created_at"], datetime) else str(result["created_at"])
        })
    
    return {"leaderboard": leaderboard}

@router.post("/buy_item")
async def buy_item(request: schemas.BuyItemRequest):
    """购买道具（简化版）"""
    user = simple_storage.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 道具价格
    item_costs = {
        "delay": 10,
        "block": 15
    }
    
    cost = item_costs.get(request.item)
    if not cost:
        raise HTTPException(status_code=400, detail="无效的道具类型")
    
    if user["points"] < cost:
        raise HTTPException(status_code=400, detail="积分不足")
    
    # 扣除积分
    simple_storage.update_user_points(request.username, -cost)
    
    # 返回更新后的积分
    updated_user = simple_storage.get_user_by_username(request.username)
    return {
        "message": "购买成功",
        "points": updated_user["points"]
    }
