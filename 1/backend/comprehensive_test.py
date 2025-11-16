#!/usr/bin/env python
import sys
import os
import requests
import time
import threading

# 设置Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backend_comprehensive():
    """综合测试后端应用和API"""
    print("=== 卡牌游戏后端综合测试 ===\n")
    
    # 测试1: 导入检查
    print("1. 测试应用组件导入...")
    try:
        from app.main import app
        print("   ✅ 应用主模块导入成功")
        
        from app.database import engine, SessionLocal
        print("   ✅ 数据库模块导入成功")
        
        from app.models import User, GameResult, Item, UserItem
        print("   ✅ 数据模型导入成功")
        
        from app import crud
        print("   ✅ CRUD操作导入成功")
        
        from app.routes import auth, game
        print("   ✅ 路由模块导入成功")
        
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试2: 数据库连接
    print("\n2. 测试数据库连接...")
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1 as test")
        print("   ✅ 数据库连接成功")
        db.close()
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return False
    
    # 测试3: 启动服务器并进行API测试
    print("\n3. 测试服务器启动和API端点...")
    
    def start_server():
        """在子线程中启动服务器"""
        try:
            import uvicorn
            uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="error")
        except Exception as e:
            print(f"   服务器启动错误: {e}")
    
    # 在新端口启动服务器进行测试
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    print("   正在启动测试服务器 (端口8001)...")
    time.sleep(3)
    
    # API测试
    base_url = "http://127.0.0.1:8001"
    
    try:
        # 健康检查
        print("   测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ 健康检查成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
        
        # 道具列表
        print("   测试道具列表...")
        response = requests.get(f"{base_url}/game/items", timeout=5)
        if response.status_code == 200:
            print("   ✅ 道具列表成功")
            items = response.json()
            print(f"   道具数量: {len(items)}")
        else:
            print(f"   ❌ 道具列表失败: {response.status_code}")
        
        # 排行榜
        print("   测试排行榜...")
        response = requests.get(f"{base_url}/game/leaderboard", timeout=5)
        if response.status_code == 200:
            print("   ✅ 排行榜成功")
            print(f"   排行榜数据: {response.json()}")
        else:
            print(f"   ❌ 排行榜失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
    
    print("\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_backend_comprehensive()