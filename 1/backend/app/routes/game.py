from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from ..main import get_db
from ..schemas import GameResultCreate, GameResultResponse, UserResponse
from ..crud import create_game_result, get_user_game_history
from ..auth import get_current_user  # 导入当前用户依赖
from ..models import User  # 导入User模型

router = APIRouter(
    prefix="/game",  # 路由前缀
    tags=["game"]    # 分组标签
)

@router.post("/result", response_model=GameResultResponse, status_code=status.HTTP_201_CREATED)
def upload_game_result(
    result: GameResultCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]  # 依赖：必须登录
):
    """上传游戏结果（需要认证）"""
    # 验证数据合理性（示例：时间和步数必须为正数）
    if result.time_seconds <= 0 or result.steps <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time and steps must be positive numbers"
        )
    # 创建结果（关联当前用户ID）
    return create_game_result(db=db, result=result, user_id=current_user.id)

@router.get("/history", response_model=List[GameResultResponse])
def get_game_history(
    skip: int = 0,  # 分页参数：跳过前N条
    limit: int = 10,  # 分页参数：最多返回N条
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]  # 仅能查询自己的历史
):
    """查询当前用户的游戏历史（需要认证）"""
    history = get_user_game_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return history