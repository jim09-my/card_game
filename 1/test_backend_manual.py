#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动测试后端服务启动
用于诊断后端服务启动问题
"""
import os
import sys
import subprocess
import time
import requests

def test_backend_startup():
    """测试后端服务启动"""
    print("=" * 50)
    print("后端服务启动测试")
    print("=" * 50)
    print()
    
    # 获取后端目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(current_dir, "backend")
    
    print(f"后端目录: {backend_dir}")
    print(f"Python路径: {sys.executable}")
    print()
    
    # 检查目录
    if not os.path.exists(backend_dir):
        print(f"❌ 后端目录不存在: {backend_dir}")
        return False
    
    start_server_path = os.path.join(backend_dir, "start_server.py")
    if not os.path.exists(start_server_path):
        print(f"❌ 启动脚本不存在: {start_server_path}")
        return False
    
    print("✅ 目录和文件检查通过")
    print()
    
    # 测试导入
    print("测试后端模块导入...")
    try:
        sys.path.insert(0, backend_dir)
        from app.main import app
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("启动后端服务...")
    print("（按 Ctrl+C 停止）")
    print()
    
    # 启动服务
    try:
        process = subprocess.Popen(
            [sys.executable, "start_server.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 读取输出
        output_lines = []
        max_wait = 30
        started = False
        
        for i in range(max_wait):
            # 检查进程
            if process.poll() is not None:
                print(f"\n❌ 进程已退出，返回码: {process.returncode}")
                remaining = process.stdout.read()
                if remaining:
                    output_lines.extend(remaining.splitlines())
                break
            
            # 读取输出
            try:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    print(f"[后端] {line}")
            except:
                pass
            
            # 检查服务
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print(f"\n✅ 后端服务启动成功！")
                    print(f"   访问地址: http://localhost:8000/docs")
                    started = True
                    break
            except:
                pass
            
            time.sleep(1)
        
        if not started:
            if process.poll() is None:
                print(f"\n⚠️  服务可能未正常启动（等待{max_wait}秒）")
            else:
                print(f"\n❌ 服务启动失败")
                if output_lines:
                    print("\n错误输出:")
                    for line in output_lines[-20:]:
                        if line.strip():
                            print(f"  {line}")
        
        # 保持运行
        if started:
            print("\n服务正在运行，按 Ctrl+C 停止...")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n正在停止服务...")
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
                print("服务已停止")
        
        return started
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        test_backend_startup()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()

