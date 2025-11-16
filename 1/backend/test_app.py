#!/usr/bin/env python
import sys
import os

# 设置Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app():
    """测试后端应用是否可以正常导入和初始化"""
    try:
        print("测试应用导入...")
        
        # 导入应用组件
        from app.main import app
        print("✓ 应用导入成功")
        
        # 导入数据库
        from app.database import engine, SessionLocal
        from app.models import User, GameResult, Item, UserItem
        print("✓ 数据库模型导入成功")
        
        # 导入CRUD
        from app import crud
        print("✓ CRUD操作导入成功")
        
        # 导入路由
        from app.routes import auth, game
        print("✓ 路由导入成功")
        
        # 测试数据库连接
        db = SessionLocal()
        try:
            result = db.execute("SELECT 1")
            print("✓ 数据库连接测试成功")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            return False
        finally:
            db.close()
        
        print("\n所有测试通过！应用可以正常启动。")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app()