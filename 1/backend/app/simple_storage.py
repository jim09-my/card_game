"""
简化的内存存储，替代数据库
最多支持10个用户
"""
from datetime import datetime
from typing import Optional, Dict, List
import hashlib

# 简化的密码加密（仅用于课设演示，不用于生产环境）
def _hash_password(password: str) -> str:
    """简单的密码哈希（仅用于演示）"""
    return hashlib.sha256(password.encode()).hexdigest()

# 内存存储
users: Dict[str, Dict] = {}  # username -> user_data
game_results: List[Dict] = []  # 游戏结果列表
MAX_USERS = 10  # 最多10个用户

def get_password_hash(password: str) -> str:
    """加密密码（简化版，仅用于演示）"""
    return _hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（简化版，仅用于演示）"""
    return _hash_password(plain_password) == hashed_password

def create_user(username: str, password: str) -> Optional[Dict]:
    """创建用户"""
    # 检查用户数量限制
    if len(users) >= MAX_USERS:
        return None
    
    # 检查用户名是否已存在
    if username in users:
        return None
    
    # 创建新用户
    user_id = len(users) + 1
    hashed_password = get_password_hash(password)
    user_data = {
        "id": user_id,
        "username": username,
        "hashed_password": hashed_password,
        "points": 0,
        "created_at": datetime.now()
    }
    users[username] = user_data
    return user_data

def get_user_by_username(username: str) -> Optional[Dict]:
    """根据用户名获取用户"""
    return users.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """验证用户"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def update_user_points(username: str, points: int):
    """更新用户积分"""
    if username in users:
        users[username]["points"] += points
        return users[username]["points"]
    return None

def add_game_result(username: str, game_mode: str, time_seconds: int, steps: int, score: int = 0):
    """添加游戏结果"""
    result = {
        "id": len(game_results) + 1,
        "username": username,
        "game_mode": game_mode,
        "time_seconds": time_seconds,
        "steps": steps,
        "score": score,
        "created_at": datetime.now()
    }
    game_results.append(result)
    return result

def get_user_game_history(username: str, limit: int = 100) -> List[Dict]:
    """获取用户游戏历史"""
    user_results = [r for r in game_results if r["username"] == username]
    return sorted(user_results, key=lambda x: x["created_at"], reverse=True)[:limit]

def get_leaderboard(game_mode: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """获取排行榜"""
    results = game_results.copy()
    if game_mode:
        results = [r for r in results if r["game_mode"] == game_mode]
    
    # 按时间排序
    results.sort(key=lambda x: x["time_seconds"])
    return results[:limit]

