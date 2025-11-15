from sqlalchemy.orm import Session
from .models import User, GameResult
from .schemas import UserCreate, GameResultCreate

# 已有的用户相关函数...
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    # 已有逻辑不变...
    pass

# 新增游戏结果相关函数
def create_game_result(db: Session, result: GameResultCreate, user_id: int):
    """创建游戏结果（关联用户ID）"""
    db_result = GameResult(
        **result.dict(),  # 解包time_seconds和steps
        user_id=user_id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_user_game_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """查询指定用户的游戏历史（支持分页）"""
    return db.query(GameResult).filter(
        GameResult.user_id == user_id
    ).order_by(
        GameResult.created_at.desc()  # 按时间倒序（最新的在前）
    ).offset(skip).limit(limit).all()

# 在crud.py中新增
def get_user_by_id(db: Session, user_id: int):
    """通过ID查询用户"""
    return db.query(User).filter(User.id == user_id).first()