#!/usr/bin/env python3
"""
依赖安装和测试脚本
"""
import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def test_imports():
    """测试模块导入"""
    modules = [
        ('pygame', '游戏界面'),
        ('ui', '用户界面模块'),
        ('modes.simple_mode', '简单模式'),
        ('modes.dynamic_maze', '动态迷宫模式')
    ]
    
    results = []
    for module_name, description in modules:
        try:
            __import__(module_name)
            results.append(f"✅ {description}: 导入成功")
        except ImportError as e:
            results.append(f"❌ {description}: {e}")
        except Exception as e:
            results.append(f"⚠️  {description}: 其他错误 - {e}")
    
    return results

def main():
    print("=== 卡牌游戏依赖检测和安装 ===")
    print()
    
    # 要安装的包列表
    packages = [
        'pygame',
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'passlib[bcrypt]',
        'python-jose[cryptography]',
        'pydantic',
        'python-multipart',
        'dotenv'
    ]
    
    print("1. 安装依赖包...")
    for package in packages:
        print(f"正在安装: {package}")
        if install_package(package):
            print(f"   ✅ {package} 安装成功")
        else:
            print(f"   ❌ {package} 安装失败")
    
    print()
    print("2. 测试模块导入...")
    results = test_imports()
    for result in results:
        print(f"   {result}")
    
    print()
    print("3. 检查游戏文件...")
    game_files = [
        'main.py',
        'ui.py',
        'modes/simple_mode.py',
        'modes/dynamic_maze.py'
    ]
    
    for file_path in game_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} 存在")
        else:
            print(f"   ❌ {file_path} 不存在")
    
    print()
    print("=== 检查完成 ===")

if __name__ == "__main__":
    main()