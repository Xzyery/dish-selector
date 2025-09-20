#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

# 复制相关的常量和函数
DISHES_FILE = 'dishes.json'
ORDERS_DIR = '../orders'

def load_dishes():
    """加载菜品数据"""
    if not os.path.exists(DISHES_FILE):
        with open(DISHES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(DISHES_FILE, 'r', encoding='utf-8') as f:
            dishes = json.load(f)
            # 为旧数据添加默认价格
            for dish in dishes:
                if 'price' not in dish:
                    dish['price'] = 52  # 默认价格52宝宝币
            return dishes
    except:
        return []

def load_orders():
    """加载所有订单"""
    orders = []
    if os.path.exists(ORDERS_DIR):
        for filename in os.listdir(ORDERS_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(ORDERS_DIR, filename), 'r', encoding='utf-8') as f:
                        order = json.load(f)
                        orders.append(order)
                except:
                    continue
    return sorted(orders, key=lambda x: x.get('timestamp', 0), reverse=True)

if __name__ == "__main__":
    print("=== 调试厨师端数据 ===")
    
    # 检查 dishes
    print("\n检查 dishes:")
    dishes = load_dishes()
    print(f"dishes 类型: {type(dishes)}")
    print(f"dishes 内容: {dishes}")
    print(f"是否可迭代: {hasattr(dishes, '__iter__')}")
    
    # 检查 orders
    print("\n检查 orders:")
    orders = load_orders()
    print(f"orders 类型: {type(orders)}")
    print(f"orders 内容: {orders}")
    print(f"是否可迭代: {hasattr(orders, '__iter__')}")
    
    # 测试 length 过滤器
    print("\n测试 length:")
    try:
        print(f"len(dishes): {len(dishes)}")
        print(f"len(orders): {len(orders)}")
    except Exception as e:
        print(f"长度计算错误: {e}")
    
    # 检查每个订单的结构
    print("\n检查订单结构:")
    for i, order in enumerate(orders):
        print(f"订单 {i}: {order.keys()}")
        if 'dishes' in order:
            print(f"  dishes 类型: {type(order['dishes'])}")
            try:
                print(f"  dishes 长度: {len(order['dishes'])}")
            except Exception as e:
                print(f"  dishes 长度错误: {e}")
        if 'items' in order:
            print(f"  items 类型: {type(order['items'])}")
            try:
                print(f"  items 长度: {len(order['items'])}")
            except Exception as e:
                print(f"  items 长度错误: {e}")