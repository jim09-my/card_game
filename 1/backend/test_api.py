#!/usr/bin/env python
import sys
import os

# 设置Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_requests():
    """测试requests库和API连接"""
    try:
        import requests
        print("✓ requests库导入成功")
        
        # 测试健康检查端点
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            print(f"✓ 健康检查成功: {response.status_code}")
            print(f"响应: {response.json()}")
        except Exception as e:
            print(f"✗ 健康检查失败: {e}")
            
        # 测试道具列表端点
        try:
            response = requests.get('http://localhost:8000/game/items', timeout=5)
            print(f"✓ 道具列表成功: {response.status_code}")
            print(f"道具: {response.json()}")
        except Exception as e:
            print(f"✗ 道具列表失败: {e}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_requests()