from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas
from ..auth import get_current_user, get_db

router = APIRouter(prefix="/game", tags=["game"])

@router.post("/upload_result", response_model=schemas.GameResultResponse)
async def upload_game_result(
    result: schemas.GameResultCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传游戏结果"""
    # 创建游戏结果
    db_result = crud.create_game_result(db=db, result=result, user_id=current_user.id)
    
    # 计算积分（根据游戏时间和步数计算）
    # 简单模式：120秒内完成且步数少于50 = 10积分；否则5积分
    # 困难模式：180秒内完成且步数少于100 = 20积分；否则10积分
    if result.game_mode == "simple":
        points = 10 if (result.time_seconds <= 120 and result.steps <= 50) else 5
    else:  # hard mode
        points = 20 if (result.time_seconds <= 180 and result.steps <= 100) else 10
    
    # 更新用户积分
    crud.update_user_points(db, current_user.id, points)
    
    return db_result

@router.get("/history", response_model=List[schemas.GameResultResponse])
async def get_game_history(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的游戏历史记录"""
    return crud.get_user_game_history(db, current_user.id, skip, limit)

@router.get("/best_records", response_model=schemas.UserBestRecords)
async def get_user_best_records(
    game_mode: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户最佳记录"""
    return crud.get_user_best_records(db, current_user.id, game_mode)

@router.get("/leaderboard")
async def get_leaderboard(
    game_mode: str = None,  # "simple" 或 "hard"
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取全球排行榜（按时间排序）"""
    # 查询所有用户的游戏记录
    query = db.query(crud.GameResult)
    if game_mode:
        query = query.filter(crud.GameResult.game_mode == game_mode)
    
    results = query.order_by(crud.GameResult.time_seconds.asc()).limit(limit).all()
    
    # 转换为响应格式，包含用户信息
    leaderboard = []
    for result in results:
        user = db.query(crud.User).filter(crud.User.id == result.user_id).first()
        leaderboard.append({
            "username": user.username,
            "time_seconds": result.time_seconds,
            "steps": result.steps,
            "game_mode": result.game_mode,
            "score": result.score,
            "date": result.created_at
        })
    
    return {"leaderboard": leaderboard}

@router.get("/leaderboard/steps")
async def get_steps_leaderboard(
    game_mode: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取全球排行榜（按步数排序）"""
    query = db.query(crud.GameResult)
    if game_mode:
        query = query.filter(crud.GameResult.game_mode == game_mode)
    
    results = query.order_by(crud.GameResult.steps.asc()).limit(limit).all()
    
    leaderboard = []
    for result in results:
        user = db.query(crud.User).filter(crud.User.id == result.user_id).first()
        leaderboard.append({
            "username": user.username,
            "time_seconds": result.time_seconds,
            "steps": result.steps,
            "game_mode": result.game_mode,
            "score": result.score,
            "date": result.created_at
        })
    
    return {"leaderboard": leaderboard}

# 道具相关路由
@router.get("/items", response_model=List[schemas.ItemResponse])
async def get_all_items(
    db: Session = Depends(get_db)
):
    """获取所有可用道具"""
    return crud.get_all_items(db)

@router.post("/purchase_item")
async def purchase_item(
    request: schemas.PurchaseItemRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """购买道具"""
    result = crud.purchase_item(db, current_user.id, request.item_id)
    if result is None:
        raise HTTPException(status_code=400, detail="购买失败：积分不足或道具不存在")
    
    return {"message": "购买成功", "remaining_points": current_user.points}

@router.get("/my_items", response_model=schemas.UserItemsResponse)
async def get_user_items(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户拥有的道具"""
    user_items = crud.get_user_items(db, current_user.id)
    
    # 转换为响应格式，嵌套道具信息
    response_items = []
    for user_item in user_items:
        response_items.append({
            "id": user_item.id,
            "user_id": user_item.user_id,
            "item": {
                "id": user_item.item.id,
                "name": user_item.item.name,
                "description": user_item.item.description,
                "cost": user_item.item.cost,
                "effect": user_item.item.effect,
                "created_at": user_item.item.created_at
            },
            "quantity": user_item.quantity,
            "created_at": user_item.created_at
        })
    
    return {"items": response_items}

@router.post("/use_item")
async def use_item(
    request: schemas.UseItemRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """使用道具"""
    item = crud.use_item(db, current_user.id, request.item_name)
    if item is None:
        raise HTTPException(status_code=400, detail="道具使用失败：道具不存在或数量不足")
    
    return {"message": f"成功使用道具: {item.name}", "effect": item.effect}