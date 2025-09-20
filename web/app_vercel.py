from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
import os
import json
import uuid
import math
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import shutil
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dish_selector_secret_key_2024')

# 配置文件上传 - Vercel环境下禁用
UPLOAD_FOLDER = '/tmp'  # Vercel允许写入/tmp目录
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 数据文件路径 - 从环境变量或默认值读取
base_dir = os.path.dirname(os.path.abspath(__file__))

# 内存中的数据存储 - 用于Vercel无服务器环境
_memory_storage = {
    'user_data': None,
    'dishes': None,
    'questionnaire_responses': {},
    'seeds_data': None
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
        }
    }

def load_user_data():
    """加载用户数据 - 使用内存存储"""
    global _memory_storage
    if _memory_storage['user_data'] is None:
        # 尝试从文件加载，如果失败则使用默认数据
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
    # 在Vercel环境中，我们不能写入文件，所以只存储在内存中
    print("Data saved to memory (file writing disabled in serverless environment)")

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
                _memory_storage['dishes'] = []
        except Exception as e:
            print(f"Error loading dishes: {e}")
            _memory_storage['dishes'] = []
    
    return _memory_storage['dishes']

def save_dishes(dishes):
    """保存菜品数据 - 只更新内存存储"""
    global _memory_storage
    _memory_storage['dishes'] = dishes
    print("Dishes saved to memory (file writing disabled in serverless environment)")

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
                # 默认种子数据
                _memory_storage['seeds_data'] = {
                    "seeds": {
                        "test_seed": {
                            "id": "test_seed",
                            "name": "测试种子",
                            "description": "一种神奇的种子，需要浇水一次并施肥一次才能成熟",
                            "price": 10,
                            "required_water_count": 1,
                            "required_fertilizer_count": 1,
                            "growth_time_minutes": 1,
                            "harvest_items": [
                                {"type": "coin", "amount": 20},
                                {"type": "exp", "amount": 10}
                            ]
                        }
                    }
                }
        except Exception as e:
            print(f"Error loading seeds data: {e}")
            _memory_storage['seeds_data'] = {"seeds": {}}
    
    return _memory_storage['seeds_data']

def save_seeds_data(data):
    """保存种子数据 - 只更新内存存储"""
    global _memory_storage
    _memory_storage['seeds_data'] = data
    print("Seeds data saved to memory (file writing disabled in serverless environment)")

# 基本路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/customer')
def customer():
    """客户端页面"""
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

@app.route('/chef')
def chef():
    """厨师端页面"""
    dishes = load_dishes()
    user_data = load_user_data()
    return render_template('chef.html', dishes=dishes, user_data=user_data)

# API路由 - 简化版本，避免文件操作
@app.route('/api/user_data')
def get_user_data():
    """获取用户数据API"""
    return jsonify(load_user_data())

@app.route('/api/dishes')
def get_dishes():
    """获取菜品数据API"""
    return jsonify(load_dishes())

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """添加到购物车 - 简化版本"""
    try:
        data = request.get_json()
        dish_id = data.get('dish_id')
        quantity = int(data.get('quantity', 1))
        
        # 在实际应用中，这里应该将商品添加到用户的购物车
        # 由于是内存存储，我们只返回成功响应
        
        return jsonify({
            'success': True,
            'message': f'已添加 {quantity} 个商品到购物车'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加失败: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'message': 'WXZY点餐系统 running on Vercel',
        'memory_storage': {
            'user_data_loaded': _memory_storage['user_data'] is not None,
            'dishes_loaded': _memory_storage['dishes'] is not None,
            'seeds_data_loaded': _memory_storage['seeds_data'] is not None
        }
    })

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