"""
本地存储系统 - 替代后端
使用JSON文件存储所有数据
"""
import json
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, List

STORAGE_FILE = "game_data.json"

class LocalStorage:
    """本地存储管理器"""
    
    def __init__(self, storage_file: str = STORAGE_FILE):
        self.storage_file = storage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载数据文件"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_data()
        return self._init_data()
    
    def _init_data(self) -> Dict:
        """初始化数据结构"""
        return {
            "users": {},  # username -> user_data
            "game_results": [],  # 游戏记录列表
            "max_users": 10
        }
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希（仅用于演示）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ========== 用户管理 ==========
    
    def register_user(self, username: str, password: str) -> Dict:
        """注册用户"""
        users = self.data["users"]
        
        # 检查用户数量限制
        if len(users) >= self.data["max_users"]:
            raise Exception(f"用户数量已达上限（最多{self.data['max_users']}人）")
        
        # 检查用户名是否已存在
        if username in users:
            raise Exception("用户名已存在")
        
        # 创建新用户
        user_id = len(users) + 1
        user_data = {
            "id": user_id,
            "username": username,
            "password_hash": self._hash_password(password),
            "points": 50,  # 新用户初始积分
            "items": {
                "delay": 0,  # 延时道具数量
                "block": 0,  # 阻挡道具数量
                "reveal": 0  # 直接翻牌道具数量
            },
            "created_at": datetime.now().isoformat()
        }
        users[username] = user_data
        self._save_data()
        
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "points": user_data["points"],
            "created_at": user_data["created_at"]
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """验证用户"""
        users = self.data["users"]
        if username not in users:
            return None
        
        user = users[username]
        password_hash = self._hash_password(password)
        
        if user["password_hash"] != password_hash:
            return None
        
        return {
            "id": user["id"],
            "username": user["username"],
            "points": user["points"],
            "items": user["items"],
            "created_at": user["created_at"]
        }
    
    def get_user(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        users = self.data["users"]
        if username not in users:
            return None
        
        user = users[username]
        return {
            "id": user["id"],
            "username": user["username"],
            "points": user["points"],
            "items": user["items"],
            "created_at": user["created_at"]
        }
    
    def update_user_points(self, username: str, points: int):
        """更新用户积分"""
        users = self.data["users"]
        if username in users:
            users[username]["points"] += points
            self._save_data()
            return users[username]["points"]
        return None
    
    def buy_item(self, username: str, item_type: str, cost: int) -> bool:
        """购买道具"""
        users = self.data["users"]
        if username not in users:
            return False
        
        user = users[username]
        if user["points"] < cost:
            return False
        
        user["points"] -= cost
        if item_type in user["items"]:
            user["items"][item_type] += 1
        else:
            user["items"][item_type] = 1
        
        self._save_data()
        return True
    
    def use_item(self, username: str, item_type: str) -> bool:
        """使用道具"""
        users = self.data["users"]
        if username not in users:
            return False
        
        user = users[username]
        if item_type not in user["items"] or user["items"][item_type] <= 0:
            return False
        
        user["items"][item_type] -= 1
        self._save_data()
        return True
    
    # ========== 游戏记录 ==========
    
    def add_game_result(self, username: str, game_mode: str, time_seconds: int, 
                       steps: int, score: int = 0, result: str = "victory"):
        """添加游戏结果"""
        result_data = {
            "id": len(self.data["game_results"]) + 1,
            "username": username,
            "game_mode": game_mode,
            "time_seconds": time_seconds,
            "steps": steps,
            "score": score,
            "result": result,
            "created_at": datetime.now().isoformat()
        }
        self.data["game_results"].append(result_data)
        self._save_data()
        return result_data
    
    def get_user_history(self, username: str, limit: int = 100) -> List[Dict]:
        """获取用户游戏历史"""
        results = [r for r in self.data["game_results"] if r["username"] == username]
        return sorted(results, key=lambda x: x["created_at"], reverse=True)[:limit]
    
    def get_leaderboard(self, game_mode: Optional[str] = None, sort_by: str = "time", limit: int = 10) -> List[Dict]:
        """获取排行榜
        sort_by: "time" 按时间排序, "steps" 按步数排序
        """
        results = self.data["game_results"].copy()
        
        # 过滤游戏模式
        if game_mode:
            results = [r for r in results if r["game_mode"] == game_mode]
        
        # 只包含胜利的记录
        results = [r for r in results if r["result"] == "victory"]
        
        # 排序
        if sort_by == "time":
            results.sort(key=lambda x: x["time_seconds"])
        elif sort_by == "steps":
            results.sort(key=lambda x: x["steps"])
        
        return results[:limit]
    
    def get_user_best_records(self, username: str, game_mode: Optional[str] = None) -> Dict:
        """获取用户最佳记录"""
        user_results = [r for r in self.data["game_results"] 
                       if r["username"] == username and r["result"] == "victory"]
        
        if game_mode:
            user_results = [r for r in user_results if r["game_mode"] == game_mode]
        
        if not user_results:
            return {
                "fastest_time": None,
                "fastest_time_date": None,
                "fewest_steps": None,
                "fewest_steps_date": None,
                "total_games": 0
            }
        
        fastest = min(user_results, key=lambda x: x["time_seconds"])
        fewest = min(user_results, key=lambda x: x["steps"])
        
        return {
            "fastest_time": fastest["time_seconds"],
            "fastest_time_date": fastest["created_at"],
            "fewest_steps": fewest["steps"],
            "fewest_steps_date": fewest["created_at"],
            "total_games": len(user_results)
        }

