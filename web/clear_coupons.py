#!/usr/bin/env python3
"""
清空用户优惠券的脚本
"""
import json
import os

def clear_coupons():
    # 用户数据文件路径
    user_data_path = "user_data.json"
    
    # 检查文件是否存在
    if not os.path.exists(user_data_path):
        print(f"错误：找不到文件 {user_data_path}")
        return False
    
    # 备份原文件
    backup_path = "user_data.json.backup"
    try:
        with open(user_data_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已创建备份文件: {backup_path}")
    except Exception as e:
        print(f"❌ 创建备份失败: {e}")
        return False
    
    # 读取用户数据
    try:
        with open(user_data_path, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取用户数据失败: {e}")
        return False
    
    # 统计优惠券数量
    if 'coupons' in user_data:
        total_coupons = len(user_data['coupons'])
        used_coupons = sum(1 for coupon in user_data['coupons'] if coupon.get('used', False))
        unused_coupons = total_coupons - used_coupons
        
        print(f"📊 优惠券统计:")
        print(f"   总计: {total_coupons} 张")
        print(f"   已使用: {used_coupons} 张")
        print(f"   未使用: {unused_coupons} 张")
        
        # 清空优惠券
        user_data['coupons'] = []
        print(f"🗑️  已清空所有优惠券")
    else:
        print("⚠️  用户数据中没有找到优惠券字段")
        return False
    
    # 保存修改后的数据
    try:
        with open(user_data_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存修改到 {user_data_path}")
        return True
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始清空用户优惠券...")
    
    if clear_coupons():
        print("\n✅ 优惠券清空完成！")
        print("   点餐界面将不再显示任何可用优惠券")
        print("   背包中的优惠券删除功能也会正常工作")
    else:
        print("\n❌ 优惠券清空失败，请检查错误信息")