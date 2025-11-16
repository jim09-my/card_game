#!/usr/bin/env python3
"""
简化的API测试脚本
"""
import requests
import time
import sys
import traceback

def main():
    """测试API端点"""
    print("=== 卡牌游戏后端API测试 ===")
    print()
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    base_url = "http://localhost:8000"
    
    tests = [
        ("健康检查", "/health"),
        ("道具列表", "/game/items"),
        ("排行榜", "/game/leaderboard"),
        ("步数排行榜", "/game/leaderboard/steps")
    ]
    
    for test_name, endpoint in tests:
        print(f"测试 {test_name}:")
        try:
            response = requests.get(base_url + endpoint, timeout=10)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 成功")
                if endpoint == "/health":
                    data = response.json()
                    print(f"  响应: {data}")
                elif "leaderboard" in endpoint:
                    data = response.json()
                    print(f"  数据: {len(data)} 条记录")
                    if data:
                        print(f"  示例: {data[0] if isinstance(data, list) else data}")
                else:
                    data = response.json()
                    print(f"  数据: {len(data)} 项")
                    if data:
                        print(f"  示例: {data[0] if isinstance(data, list) else data}")
            else:
                print(f"  ❌ 失败")
                print(f"  错误: {response.text}")
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            traceback.print_exc()
        print()

if __name__ == "__main__":
    main()