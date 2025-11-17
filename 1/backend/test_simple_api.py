#!/usr/bin/env python
"""
测试简化版后端API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_register():
    """测试注册"""
    print("\n测试注册...")
    try:
        data = {
            "username": "testuser",
            "password": "test123"
        }
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=data,
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        if response.status_code in [200, 201]:
            print("注册成功！")
            return True
        else:
            print(f"注册失败: {response.json()}")
            return False
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """测试登录"""
    print("\n测试登录...")
    try:
        data = {
            "username": "testuser",
            "password": "test123"
        }
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=data,
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Token: {token_data.get('access_token', 'N/A')[:20]}...")
            return token_data.get("access_token")
        else:
            print(f"登录失败: {response.json()}")
            return None
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("测试简化版后端API")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health():
        print("\n❌ 后端服务未启动或无法访问！")
        print("请先启动后端服务：")
        print("  cd backend")
        print("  python start_server.py")
        exit(1)
    
    # 测试注册
    if test_register():
        # 测试登录
        token = test_login()
        if token:
            print("\n✅ 所有测试通过！")
        else:
            print("\n⚠️ 注册成功，但登录失败")
    else:
        print("\n❌ 注册测试失败")

