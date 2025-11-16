#!/usr/bin/env python3
"""
快速测试pygame安装状态
"""
import sys
import os

print("Python版本:", sys.version)
print("Python路径:", sys.executable)
print("当前目录:", os.getcwd())

print("\n尝试导入pygame...")
try:
    import pygame
    print("✅ pygame导入成功!")
    print("pygame版本:", pygame.version.ver)
    print("pygame路径:", pygame.__file__)
    
    # 测试pygame初始化
    print("\n测试pygame初始化...")
    pygame.init()
    print("✅ pygame初始化成功")
    
    # 获取pygame显示模式信息
    print("\npygame显示模式信息:")
    info = pygame.display.Info()
    print(f"  当前分辨率: {info.current_w}x{info.current_h}")
    print(f"  像素格式: {info.bitsize}")
    
except ImportError as e:
    print("❌ pygame导入失败!")
    print("错误信息:", str(e))
    
    print("\n尝试安装pygame...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("✅ pygame安装完成!")
        
        # 再次尝试导入
        import pygame
        print("✅ 重新导入成功!")
        print("pygame版本:", pygame.version.ver)
        
    except Exception as install_error:
        print("❌ pygame安装失败:", str(install_error))

except Exception as e:
    print("❌ pygame测试失败:", str(e))

print("\n检查项目文件...")
required_files = [
    "main.py",
    "ui.py", 
    "modes/simple_mode.py",
    "modes/dynamic_maze.py"
]

for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file} 存在")
    else:
        print(f"❌ {file} 不存在")

print("\n测试完成!")