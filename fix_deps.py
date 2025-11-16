#!/usr/bin/env python3
"""
完整的游戏依赖诊断和解决方案
解决 ModuleNotFoundError: No module named 'pygame' 问题
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_python_info():
    """检查Python环境信息"""
    print("=== Python环境检查 ===")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"平台: {platform.platform()}")
    print(f"架构: {platform.machine()}")
    print()

def check_packages():
    """检查已安装的包"""
    print("=== 已安装的包检查 ===")
    returncode, stdout, stderr = run_command("pip list")
    if returncode == 0:
        lines = stdout.split('\n')
        for line in lines:
            if 'pygame' in line.lower() or 'fastapi' in line.lower() or 'uvicorn' in line.lower():
                print(f"📦 {line}")
    else:
        print(f"❌ 无法获取包列表: {stderr}")
    print()

def install_deps():
    """安装所有依赖"""
    print("=== 安装依赖包 ===")
    
    # 基本Python包
    basic_packages = [
        "pygame",
        "fastapi", 
        "uvicorn[standard]",
        "sqlalchemy",
        "passlib[bcrypt]",
        "python-jose[cryptography]", 
        "pydantic",
        "python-multipart",
        "python-dotenv"
    ]
    
    for package in basic_packages:
        print(f"🔄 安装 {package}...")
        returncode, stdout, stderr = run_command(f'"{sys.executable}" -m pip install {package}')
        
        if returncode == 0:
            print(f"✅ {package} 安装成功")
        else:
            print(f"❌ {package} 安装失败: {stderr}")
    
    print()

def test_game_imports():
    """测试游戏模块导入"""
    print("=== 游戏模块导入测试 ===")
    
    # 切换到游戏目录
    game_dir = os.path.join(os.getcwd(), '1')
    
    # 测试基本导入
    tests = [
        ("import pygame", "pygame基础导入"),
        ("import sys, os", "系统模块导入"),
        ("from modes.simple_mode import SimpleGame", "简单模式导入"),
        ("from modes.dynamic_maze import DynamicMazeGame", "动态迷宫导入"),
        ("from ui import GameUI", "UI模块导入")
    ]
    
    for test_code, description in tests:
        print(f"🔄 测试: {description}")
        cmd = f'cd 1 && python -c "{test_code}"'
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode == 0:
            print(f"✅ {description} - 成功")
        else:
            print(f"❌ {description} - 失败")
            if stderr:
                print(f"   错误: {stderr}")
    
    print()

def run_game():
    """尝试运行游戏"""
    print("=== 尝试运行游戏 ===")
    game_dir = os.path.join(os.getcwd(), '1')
    
    print("🔄 启动游戏...")
    returncode, stdout, stderr = run_command("cd 1 && python main.py", cwd=game_dir)
    
    if returncode == 0:
        print("✅ 游戏启动成功！")
        if stdout:
            print("输出:", stdout)
    else:
        print("❌ 游戏启动失败")
        if stderr:
            print("错误:", stderr)
        if stdout:
            print("输出:", stdout)
    
    print()

def create_requirements():
    """创建requirements.txt"""
    print("=== 创建requirements.txt ===")
    
    requirements_content = """# 卡牌游戏依赖
pygame==2.5.2
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
pydantic==2.5.0
python-multipart==0.0.6
python-dotenv==1.0.0
"""
    
    # 写入根目录requirements.txt
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt 创建成功")
    print()

def main():
    """主函数"""
    print("🎮 卡牌游戏依赖完整诊断和修复")
    print("="*50)
    print()
    
    # 1. 检查Python环境
    check_python_info()
    
    # 2. 检查当前包状态
    check_packages()
    
    # 3. 安装依赖
    install_deps()
    
    # 4. 再次检查包状态
    check_packages()
    
    # 5. 测试导入
    test_game_imports()
    
    # 6. 创建requirements.txt
    create_requirements()
    
    # 7. 尝试运行游戏
    run_game()
    
    print("="*50)
    print("🎉 诊断和修复完成！")
    print()
    print("如果还有问题，请检查:")
    print("1. Python版本是否兼容 (建议 3.8+)")
    print("2. 是否有管理员权限安装包")
    print("3. 是否有网络连接下载包")

if __name__ == "__main__":
    main()