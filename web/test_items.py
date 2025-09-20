#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试物品使用功能的脚本
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'
session = requests.Session()

def login():
    """登录测试"""
    response = session.post(f'{BASE_URL}/login', data={
        'username': 'test_user',
        'password': 'test123'
    })
    return response.status_code == 200

def test_use_physical_item():
    """测试使用物理物品"""
    print("🧪 测试使用荒野乱斗卡...")
    
    # 先获取库存
    response = session.get(f'{BASE_URL}/inventory')
    if response.status_code != 200:
        print("❌ 无法访问库存页面")
        return False
    
    # 模拟使用第一个荒野乱斗卡（假设在index 2）
    response = session.post(f'{BASE_URL}/use_item', 
                          json={'item_index': 2},
                          headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 物理物品使用结果: {result}")
        return result.get('success', False)
    else:
        print(f"❌ 物理物品使用失败: {response.status_code}")
        return False

def test_use_game_item():
    """测试使用游戏机会物品"""
    print("🎮 测试使用游戏机会...")
    
    # 模拟使用游戏机会道具（假设在index 0）
    response = session.post(f'{BASE_URL}/use_item', 
                          json={'item_index': 0},
                          headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 游戏物品使用结果: {result}")
        return result.get('success', False)
    else:
        print(f"❌ 游戏物品使用失败: {response.status_code}")
        return False

def check_orders():
    """检查厨师端订单"""
    print("📋 检查厨师端订单...")
    response = session.get(f'{BASE_URL}/chef')
    if response.status_code == 200:
        print("✅ 厨师端可以访问")
        return True
    else:
        print(f"❌ 厨师端访问失败: {response.status_code}")
        return False

if __name__ == '__main__':
    print("🚀 开始测试物品使用功能...")
    
    # 登录
    if login():
        print("✅ 登录成功")
    else:
        print("❌ 登录失败")
        exit(1)
    
    # 测试各种物品使用
    test_use_physical_item()
    test_use_game_item()
    check_orders()
    
    print("🏁 测试完成!")