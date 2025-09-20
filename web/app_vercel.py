from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
import os
import json
import uuid
import math
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
import shutil
import random

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 明确指定模板和静态文件路径
app = Flask(__name__, 
           template_folder=os.path.join(current_dir, 'templates'),
           static_folder=os.path.join(current_dir, 'static'))
app.secret_key = os.environ.get('SECRET_KEY', 'dish_selector_secret_key_2024')

# 配置文件上传 - Vercel环境下禁用文件上传功能
UPLOAD_FOLDER = '/tmp'  # Vercel允许写入/tmp目录
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 数据文件路径
base_dir = current_dir

# 内存中的数据存储 - 用于Vercel无服务器环境
_memory_storage = {
    'user_data': None,
    'dishes': None,
    'questionnaire_responses': {},
    'seeds_data': None,
    'orders': {}
}

# 默认用户凭据
DEFAULT_USER = {
    'username': 'wxb',
    'password': '5201314'
}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_default_user_data():
    """获取默认用户数据"""
    return {
        'balance': 520,  # 初始宝宝币余额
        'transactions': [],  # 交易记录
        'daily_questionnaire_completed': {},  # 每日问卷完成状态
        'optimism_streak': 0,  # 乐观连续天数
        'medicine_streak': 0,  # 按时吃药连续天数
        'max_optimism_streak': 0,  # 最高乐观连续天数
        'max_medicine_streak': 0,  # 最高按时吃药连续天数
        'farm_level': 1,  # 农场等级
        'farm_exp': 0,  # 农场经验
        'daily_tasks': {
            'questionnaire': False,
            'poop_photo': False,
            'lucky_spin': False
        },
        'last_reset_date': None,  # 上次重置日期
        'coupons': [],  # 优惠券列表
        'inventory': [],  # 背包物品
        'lottery_chances': 3,  # 抽奖次数
        'last_lottery_date': None,  # 上次抽奖日期
        'farm_data': {
            'planted_seeds': {},  # 已种植的种子
            'last_poop_date': None  # 最后农场打卡日期
        },
        'guess_game': {
            'chances': 3,
            'last_game_date': None
        },
        'treasure_hunt': {
            'position': 0,
            'dice_count': 1,
            'completion_rewards_claimed': [],
            'is_completed': False
        }
    }

def get_default_dishes():
    """获取默认菜品数据"""
    return [
        {
            "id": "default_dish_1",
            "name": "示例菜品",
            "description": "这是一个示例菜品，用于演示系统功能",
            "price": 15,
            "image": "",
            "category": "主食",
            "created_at": datetime.now().isoformat()
        }
    ]

def get_default_seeds_data():
    """获取默认种子数据"""
    return {
        "seeds": {
            "magic_seed": {
                "id": "magic_seed",
                "name": "魔法种子",
                "description": "一种神奇的种子，容易种植",
                "price": 10,
                "required_water_count": 1,
                "required_fertilizer_count": 1,
                "growth_time_minutes": 5,
                "harvest_items": [
                    {"type": "coin", "amount": 20},
                    {"type": "exp", "amount": 10}
                ],
                "available": True
            }
        }
    }

def load_user_data():
    """加载用户数据 - 使用内存存储"""
    global _memory_storage
    if _memory_storage['user_data'] is None:
        try:
            file_path = os.path.join(base_dir, 'user_data.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    _memory_storage['user_data'] = json.load(f)
            else:
                _memory_storage['user_data'] = get_default_user_data()
        except Exception as e:
            print(f"Error loading user data: {e}")
            _memory_storage['user_data'] = get_default_user_data()
    
    return _memory_storage['user_data']

def save_user_data(data):
    """保存用户数据 - 只更新内存存储"""
    global _memory_storage
    _memory_storage['user_data'] = data

def load_dishes():
    """加载菜品数据"""
    global _memory_storage
    if _memory_storage['dishes'] is None:
        try:
            file_path = os.path.join(base_dir, 'dishes.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    _memory_storage['dishes'] = json.load(f)
            else:
                _memory_storage['dishes'] = get_default_dishes()
        except Exception as e:
            print(f"Error loading dishes: {e}")
            _memory_storage['dishes'] = get_default_dishes()
    
    return _memory_storage['dishes']

def save_dishes(dishes):
    """保存菜品数据 - 只更新内存存储"""
    global _memory_storage
    _memory_storage['dishes'] = dishes

def load_seeds_data():
    """加载种子数据"""
    global _memory_storage
    if _memory_storage['seeds_data'] is None:
        try:
            file_path = os.path.join(base_dir, 'seeds_data.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    _memory_storage['seeds_data'] = json.load(f)
            else:
                _memory_storage['seeds_data'] = get_default_seeds_data()
        except Exception as e:
            print(f"Error loading seeds data: {e}")
            _memory_storage['seeds_data'] = get_default_seeds_data()
    
    return _memory_storage['seeds_data']

def save_seeds_data(data):
    """保存种子数据 - 只更新内存存储"""
    global _memory_storage
    _memory_storage['seeds_data'] = data

# 图片文件路由
@app.route('/images/<filename>')
def get_image(filename):
    """获取图片文件"""
    return send_from_directory(app.static_folder, filename)

# 基本路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/chef')
def chef():
    """厨师端页面"""
    try:
        dishes = load_dishes()
        user_data = load_user_data()
        return render_template('chef.html', dishes=dishes, user_data=user_data)
    except Exception as e:
        return jsonify({
            'error': 'Chef page error',
            'details': str(e),
            'template_folder': app.template_folder,
            'template_exists': os.path.exists(os.path.join(app.template_folder, 'chef.html')),
            'current_dir': os.getcwd()
        }), 500

@app.route('/customer')
def customer():
    """客户端页面"""
    try:
        dishes = load_dishes()
        user_data = load_user_data()
        
        # 检查并重置每日任务
        today = date.today().isoformat()
        if user_data.get('last_reset_date') != today:
            user_data['daily_tasks'] = {
                'questionnaire': False,
                'poop_photo': False,
                'lucky_spin': False
            }
            user_data['last_reset_date'] = today
            save_user_data(user_data)
        
        return render_template('customer.html', dishes=dishes, user_data=user_data)
    except Exception as e:
        return jsonify({
            'error': 'Customer page error',
            'details': str(e),
            'template_folder': app.template_folder,
            'template_exists': os.path.exists(os.path.join(app.template_folder, 'customer.html')),
            'current_dir': os.getcwd()
        }), 500

@app.route('/customer/<customer_id>')
def customer_with_id(customer_id):
    """带客户ID的客户端页面"""
    try:
        dishes = load_dishes()
        user_data = load_user_data()
        return render_template('customer.html', dishes=dishes, user_data=user_data, customer_id=customer_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 每日任务相关路由
@app.route('/daily_tasks')
def daily_tasks():
    """每日任务页面"""
    try:
        user_data = load_user_data()
        return render_template('daily_tasks.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 农场相关路由
@app.route('/farm')
def farm():
    """农场页面"""
    try:
        user_data = load_user_data()
        seeds_data = load_seeds_data()
        return render_template('farm.html', user_data=user_data, seeds_data=seeds_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 问卷相关路由
@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    """问卷页面"""
    try:
        user_data = load_user_data()
        if request.method == 'POST':
            # 处理问卷提交
            today = date.today().isoformat()
            user_data['daily_questionnaire_completed'][today] = True
            user_data['daily_tasks']['questionnaire'] = True
            user_data['balance'] += 20  # 完成问卷奖励
            save_user_data(user_data)
            flash('问卷已提交，获得20宝宝币奖励！', 'success')
            return redirect(url_for('customer'))
        
        return render_template('questionnaire.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 签到相关路由
@app.route('/check_in_page')
def check_in_page():
    """签到页面"""
    try:
        user_data = load_user_data()
        return render_template('check_in.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 猜谜游戏相关路由
@app.route('/guess_game')
def guess_game():
    """猜谜游戏页面"""
    try:
        user_data = load_user_data()
        return render_template('guess_game.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 抽奖相关路由
@app.route('/lottery_page')
def lottery_page():
    """抽奖页面"""
    try:
        user_data = load_user_data()
        return render_template('lottery.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 背包相关路由
@app.route('/inventory_page')
def inventory_page():
    """背包页面"""
    try:
        user_data = load_user_data()
        return render_template('inventory.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 寻宝游戏相关路由
@app.route('/treasure_hunt')
def treasure_hunt():
    """寻宝游戏页面"""
    try:
        user_data = load_user_data()
        return render_template('treasure_hunt.html', user_data=user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API 路由
@app.route('/api/user_data')
def get_user_data():
    """获取用户数据API"""
    return jsonify(load_user_data())

@app.route('/api/dishes')
def get_dishes():
    """获取菜品数据API"""
    return jsonify(load_dishes())

# 订单相关路由
@app.route('/place_order', methods=['POST'])
def place_order():
    """下订单"""
    try:
        data = request.get_json()
        order_id = str(uuid.uuid4())[:8]
        order_time = datetime.now().isoformat()
        
        # 简化的订单处理
        global _memory_storage
        if 'orders' not in _memory_storage:
            _memory_storage['orders'] = {}
        
        _memory_storage['orders'][order_id] = {
            'id': order_id,
            'items': data.get('items', []),
            'total_price': data.get('total_price', 0),
            'customer_id': data.get('customer_id', 'default'),
            'order_time': order_time,
            'status': 'pending'
        }
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': '订单提交成功！'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下单失败: {str(e)}'
        }), 500

@app.route('/get_orders')
def get_orders():
    """获取订单列表"""
    global _memory_storage
    orders = _memory_storage.get('orders', {})
    return jsonify(list(orders.values()))

@app.route('/complete_order', methods=['POST'])
def complete_order():
    """完成订单"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        global _memory_storage
        if order_id in _memory_storage.get('orders', {}):
            _memory_storage['orders'][order_id]['status'] = 'completed'
            return jsonify({'success': True, 'message': '订单已完成！'})
        else:
            return jsonify({'success': False, 'message': '订单不存在！'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 厨师端功能路由
@app.route('/add_dish', methods=['POST'])
def add_dish():
    """添加菜品"""
    try:
        data = request.get_json()
        dishes = load_dishes()
        
        new_dish = {
            'id': str(uuid.uuid4())[:8],
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'price': float(data.get('price', 0)),
            'image': '',  # 在Vercel环境中不支持图片上传
            'category': data.get('category', '其他'),
            'created_at': datetime.now().isoformat()
        }
        
        dishes.append(new_dish)
        save_dishes(dishes)
        
        return jsonify({'success': True, 'message': '菜品添加成功！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete_dish', methods=['POST'])
def delete_dish():
    """删除菜品"""
    try:
        data = request.get_json()
        dish_id = data.get('dish_id')
        dishes = load_dishes()
        
        dishes = [dish for dish in dishes if dish['id'] != dish_id]
        save_dishes(dishes)
        
        return jsonify({'success': True, 'message': '菜品删除成功！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 用户数据管理路由
@app.route('/update_balance', methods=['POST'])
def update_balance():
    """更新余额"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        user_data = load_user_data()
        user_data['balance'] += amount
        save_user_data(user_data)
        return jsonify({'success': True, 'new_balance': user_data['balance']})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 优惠券管理路由
@app.route('/chef/add_coupons', methods=['POST'])
def add_coupons():
    """添加优惠券"""
    try:
        data = request.get_json()
        coupon_type = data.get('coupon_type')
        quantity = int(data.get('quantity', 1))
        
        user_data = load_user_data()
        
        for _ in range(quantity):
            coupon = {
                'id': str(uuid.uuid4())[:8],
                'type': coupon_type,
                'name': f'{coupon_type}优惠券',
                'description': f'可享受{coupon_type}优惠',
                'created_at': datetime.now().isoformat()
            }
            user_data['coupons'].append(coupon)
            
            # 同时添加到背包
            inventory_item = {
                'id': coupon['id'],
                'name': coupon['name'],
                'type': 'coupon',
                'description': coupon['description'],
                'created_at': coupon['created_at']
            }
            user_data['inventory'].append(inventory_item)
        
        save_user_data(user_data)
        return jsonify({'success': True, 'message': f'成功添加{quantity}张{coupon_type}优惠券！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/chef/clear_all_coupons', methods=['POST'])
def clear_all_coupons():
    """清空所有优惠券"""
    try:
        user_data = load_user_data()
        user_data['coupons'] = []
        # 从背包中删除所有优惠券类型的物品
        user_data['inventory'] = [item for item in user_data['inventory'] if item.get('type') != 'coupon']
        save_user_data(user_data)
        return jsonify({'success': True, 'message': '所有优惠券已清空！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 背包管理路由
@app.route('/delete_inventory_item', methods=['POST'])
def delete_inventory_item():
    """删除背包物品"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        user_data = load_user_data()
        
        # 从背包中删除物品
        user_data['inventory'] = [item for item in user_data['inventory'] if item['id'] != item_id]
        
        # 如果是优惠券，也从优惠券列表中删除
        user_data['coupons'] = [coupon for coupon in user_data['coupons'] if coupon['id'] != item_id]
        
        save_user_data(user_data)
        return jsonify({'success': True, 'message': '物品删除成功！'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 健康检查和调试路由
@app.route('/health')
def health_check():
    """健康检查端点"""
    template_folder = app.template_folder
    static_folder = app.static_folder
    
    return jsonify({
        'status': 'ok',
        'message': 'WXZY点餐系统 running on Vercel',
        'memory_storage': {
            'user_data_loaded': _memory_storage['user_data'] is not None,
            'dishes_loaded': _memory_storage['dishes'] is not None,
            'seeds_data_loaded': _memory_storage['seeds_data'] is not None
        },
        'file_system': {
            'current_dir': os.getcwd(),
            'template_folder': template_folder,
            'static_folder': static_folder,
            'template_folder_exists': os.path.exists(template_folder) if template_folder else False,
            'static_folder_exists': os.path.exists(static_folder) if static_folder else False,
            'templates': os.listdir(template_folder) if template_folder and os.path.exists(template_folder) else []
        }
    })

@app.route('/test_template')
def test_template():
    """测试模板渲染"""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({
            'error': 'Template test failed',
            'details': str(e),
            'template_folder': app.template_folder,
            'current_dir': os.getcwd(),
            'files_in_current_dir': os.listdir('.'),
            'template_exists': os.path.exists(os.path.join(app.template_folder, 'index.html')) if app.template_folder else False
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'The application encountered an unexpected error.',
        'details': str(error)
    }), 500

if __name__ == '__main__':
    app.run(debug=True)