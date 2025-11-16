from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from .models import User, GameResult, Item, UserItem
from .schemas import UserCreate, GameResultCreate, UserUpdate, ItemCreate, UserItemCreate

# 用户相关函数
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_points(db: Session, user_id: int, points: int):
    """更新用户积分"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.points += points
        db.commit()
        db.refresh(db_user)
    return db_user

# 游戏结果相关函数
def create_game_result(db: Session, result: GameResultCreate, user_id: int):
    """创建游戏结果（关联用户ID）"""
    db_result = GameResult(
        game_mode=result.game_mode,
        time_seconds=result.time_seconds,
        steps=result.steps,
        score=result.score,
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
    ).order_by(desc(GameResult.created_at)).offset(skip).limit(limit).all()

def get_user_best_records(db: Session, user_id: int, game_mode: str = None):
    """获取用户最佳记录（最快时间、最少步数）"""
    query = db.query(GameResult).filter(GameResult.user_id == user_id)
    
    if game_mode:
        query = query.filter(GameResult.game_mode == game_mode)
    
    results = query.all()
    
    if not results:
        return None
    
    # 计算最佳记录
    fastest_time = min(results, key=lambda x: x.time_seconds)
    fewest_steps = min(results, key=lambda x: x.steps)
    
    return {
        "fastest_time": fastest_time.time_seconds,
        "fastest_time_date": fastest_time.created_at,
        "fewest_steps": fewest_steps.steps,
        "fewest_steps_date": fewest_steps.created_at,
        "total_games": len(results)
    }

# 道具相关函数
def get_all_items(db: Session):
    """获取所有可用道具"""
    return db.query(Item).all()

def get_item_by_name(db: Session, name: str):
    """根据名称获取道具"""
    return db.query(Item).filter(Item.name == name).first()

def create_item(db: Session, item: ItemCreate):
    """创建新道具"""
    db_item = Item(
        name=item.name,
        description=item.description,
        cost=item.cost,
        effect=item.effect
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def purchase_item(db: Session, user_id: int, item_id: int):
    """购买道具（消耗积分）"""
    # 获取道具信息
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return None
    
    # 获取用户信息
    user = get_user_by_id(db, user_id)
    if not user or user.points < item.cost:
        return None  # 积分不足
    
    # 检查是否已有该道具
    user_item = db.query(UserItem).filter(
        UserItem.user_id == user_id,
        UserItem.item_id == item_id
    ).first()
    
    if user_item:
        # 增加数量
        user_item.quantity += 1
    else:
        # 创建新的用户道具记录
        user_item = UserItem(
            user_id=user_id,
            item_id=item_id,
            quantity=1
        )
        db.add(user_item)
    
    # 扣除积分
    user.points -= item.cost
    
    db.commit()
    db.refresh(user_item)
    return user_item

def get_user_items(db: Session, user_id: int):
    """获取用户拥有的所有道具"""
    return db.query(UserItem).filter(UserItem.user_id == user_id).all()

def use_item(db: Session, user_id: int, item_name: str):
    """使用道具"""
    item = get_item_by_name(db, item_name)
    if not item:
        return None
    
    user_item = db.query(UserItem).filter(
        UserItem.user_id == user_id,
        UserItem.item_id == item.id
    ).first()
    
    if not user_item or user_item.quantity <= 0:
        return None
    
    # 减少道具数量
    user_item.quantity -= 1
    if user_item.quantity == 0:
        db.delete(user_item)
    
    db.commit()
    return item