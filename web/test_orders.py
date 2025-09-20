import json
import os

ORDERS_DIR = "../orders"

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
                        print(f"Loaded order {order.get('id')}: keys = {list(order.keys())}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue
    return sorted(orders, key=lambda x: x.get('timestamp', 0), reverse=True)

if __name__ == "__main__":
    orders = load_orders()
    print(f"Total orders: {len(orders)}")
    for order in orders:
        print(f"Order {order['id']}: source={order.get('source', 'normal')}, has_dishes={bool(order.get('dishes'))}, has_items={bool(order.get('items'))}")