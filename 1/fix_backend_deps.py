#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速修复后端依赖问题
"""
import subprocess
import sys

def install_package(package):
    """安装Python包"""
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"  ✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("后端依赖修复工具")
    print("=" * 50)
    print()
    
    # 必需的依赖包
    required_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "passlib[bcrypt]==1.7.4",
        "python-jose[cryptography]==3.3.0",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "requests"
    ]
    
    print("将安装以下依赖包:")
    for pkg in required_packages:
        print(f"  - {pkg}")
    print()
    
    input("按回车键开始安装...")
    print()
    
    success_count = 0
    for package in required_packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"安装完成: {success_count}/{len(required_packages)} 个包安装成功")
    print("=" * 50)
    
    if success_count == len(required_packages):
        print("\n所有依赖已安装成功！现在可以尝试运行游戏了。")
    else:
        print("\n部分依赖安装失败，请检查错误信息。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n安装被用户中断")
    except Exception as e:
        print(f"\n安装过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")

