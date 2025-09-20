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

# 配置文件上传
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 数据文件路径
DISHES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dishes.json')
ORDERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'orders')
USER_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.json')
QUESTIONNAIRE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questionnaire_responses.json')
SEEDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seeds_data.json')

# 确保必要的目录存在
for directory in [UPLOAD_FOLDER, ORDERS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 默认用户凭据（保留用于兼容性）
DEFAULT_USER = {
    'username': 'wxb',
    'password': '5201314'
}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_user_data():
    """加载用户数据"""
    default_data = {
        'balance': 520,  # 初始宝宝币余额
        'transactions': [],  # 交易记录
        'daily_questionnaire_completed': {},  # 每日问卷完成状态
        'optimism_streak': 0,  # 乐观连续天数
        'medicine_streak': 0,  # 按时吃药连续天数
        'checkin_streak': 0,  # 小打卡连续天数
        'exercise_streak': 0,  # 健身连续天数
        'check_in_history': {},  # 签到历史 {date: {'checked': True, 'reward': amount}}
        'consecutive_days': 0,  # 连续签到天数
        'total_check_ins': 0,  # 总签到天数
        'coupons': [],  # 优惠券 [{'type': 'discount', 'value': 0.9, 'description': '9折优惠券', 'expires': date, 'used': False}]
        'guess_game_history': {},  # 猜数字游戏历史 {date: {'games_played': count, 'total_reward': amount}}
        'daily_guess_games': 0,  # 今日已玩游戏次数
        'inventory': [],  # 背包物品 [{'type': 'item', 'name': '物品名', 'description': '描述', 'category': '类别', 'quantity': 数量}]
        'make_up_cards': 0,  # 补签卡数量
        'extra_game_chances': 0,  # 额外游戏机会
        'farm': {  # 农场数据
            'seeds_inventory': {},  # 种子库存 {seed_id: quantity}
            'planted_crops': [],  # 已种植作物 [{'id': 'uuid', 'seed_id': 'seed1', 'planted_date': 'date', 'last_watered': 'date', 'water_count': 0, 'fertilizer_count': 0, 'status': 'growing|mature|dead'}]
            'last_farm_visit': None,  # 最后访问农场时间
            'farm_slots': 6,  # 农场种植位数量
            'fertilizer': 0,  # 粪便数量
            'daily_poop_count': 0,  # 每日农场打卡次数
            'last_poop_date': None  # 最后农场打卡日期
        }
    }
    
    if not os.path.exists(USER_DATA_FILE):
        save_user_data(default_data)
        return default_data
    
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            
        # 确保所有必需的字段都存在
        updated = False
        for key, value in default_data.items():
            if key not in loaded_data:
                loaded_data[key] = value
                updated = True
        
        # 如果数据结构有更新，保存它
        if updated:
            save_user_data(loaded_data)
            
        return loaded_data
    except Exception as e:
        print(f"Error loading user data: {e}")
        save_user_data(default_data)
        return default_data

def save_user_data(data):
    """保存用户数据"""
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_seeds_data():
    """加载种子数据"""
    try:
        with open(SEEDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading seeds data: {e}")
        # 返回默认种子数据
        default_seeds = {
            "seeds": {
                "test_seed": {
                    "id": "test_seed",
                    "name": "测试种子",
                    "description": "一种神奇的种子，需要浇水一次并施肥一次才能成熟",
                    "price": 10,
                    "required_water_count": 1,
                    "required_fertilizer_count": 1,
                    "harvest_item": {
                        "name": "测试果实",
                        "description": "测试种子长出的神奇果实",
                        "category": "fruit"
                    },
                    "growth_stages": ["种子", "成熟"],
                    "available": True,
                    "icon": "🌱"
                },
                "tomato_seed": {
                    "id": "tomato_seed", 
                    "name": "番茄种子",
                    "description": "新鲜的番茄种子，需要浇水一次并施肥一次才能成熟",
                    "price": 15,
                    "required_water_count": 1,
                    "required_fertilizer_count": 1,
                    "harvest_item": {
                        "name": "新鲜番茄",
                        "description": "刚成熟的新鲜番茄",
                        "category": "vegetable"
                    },
                    "growth_stages": ["种子", "成熟"],
                    "available": True,
                    "icon": "🍅"
                }
            }
        }
        save_seeds_data(default_seeds)
        return default_seeds

def save_seeds_data(data):
    """保存种子数据"""
    with open(SEEDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_crop_status():
    """检查作物状态，处理死亡逻辑"""
    user_data = load_user_data()
    current_date = datetime.now().strftime('%Y-%m-%d')
    updated = False
    
    for crop in user_data['farm']['planted_crops']:
        if crop['status'] == 'growing':
            # 检查是否超过3天未浇水
            if crop['last_watered']:
                last_watered_date = datetime.strptime(crop['last_watered'], '%Y-%m-%d')
                days_since_watered = (datetime.now() - last_watered_date).days
                
                if days_since_watered >= 3:
                    crop['status'] = 'dead'
                    updated = True
            else:
                # 如果从未浇水，检查种植日期
                planted_date = datetime.strptime(crop['planted_date'], '%Y-%m-%d')
                days_since_planted = (datetime.now() - planted_date).days
                
                if days_since_planted >= 3:
                    crop['status'] = 'dead'
                    updated = True
    
    if updated:
        save_user_data(user_data)
    
    return user_data

def add_transaction(amount, description, transaction_type='income'):
    """添加交易记录"""
    user_data = load_user_data()
    
    if transaction_type == 'expense' and user_data['balance'] < amount:
        return False, '宝宝币余额不足'
    
    if transaction_type == 'expense':
        user_data['balance'] -= amount
        amount = -amount
    else:
        user_data['balance'] += amount
    
    transaction = {
        'id': str(uuid.uuid4())[:8],
        'amount': amount,
        'description': description,
        'type': transaction_type,
        'timestamp': int(datetime.now().timestamp()),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    user_data['transactions'].insert(0, transaction)  # 最新的在前面
    save_user_data(user_data)
    return True, '操作成功'

def is_questionnaire_completed_today():
    """检查今天是否已完成问卷"""
    user_data = load_user_data()
    today = date.today().isoformat()
    return today in user_data['daily_questionnaire_completed']

def mark_questionnaire_completed():
    """标记今天的问卷已完成"""
    user_data = load_user_data()
    today = date.today().isoformat()
    user_data['daily_questionnaire_completed'][today] = True
    save_user_data(user_data)

def save_questionnaire_response(responses):
    """保存问卷回答"""
    today = date.today().isoformat()
    
    # 加载现有的问卷数据
    if os.path.exists(QUESTIONNAIRE_FILE):
        try:
            with open(QUESTIONNAIRE_FILE, 'r', encoding='utf-8') as f:
                all_responses = json.load(f)
        except:
            all_responses = {}
    else:
        all_responses = {}
    
    questionnaire_data = {
        'date': today,
        'timestamp': datetime.now().isoformat(),
        'responses': responses,
        'total_reward': responses.get('total_reward', 0)
    }
    
    all_responses[today] = questionnaire_data
    
    with open(QUESTIONNAIRE_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_responses, f, ensure_ascii=False, indent=2)

def load_all_questionnaire_responses():
    """加载所有问卷回答"""
    if not os.path.exists(QUESTIONNAIRE_FILE):
        return []
    
    try:
        with open(QUESTIONNAIRE_FILE, 'r', encoding='utf-8') as f:
            all_responses = json.load(f)
            responses = list(all_responses.values())
            return sorted(responses, key=lambda x: x.get('date', ''), reverse=True)
    except:
        return []

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

def save_dishes(dishes):
    """保存菜品数据"""
    with open(DISHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(dishes, f, ensure_ascii=False, indent=2)

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

def save_order(order):
    """保存订单"""
    filename = f"order_{order['id']}.json"
    filepath = os.path.join(ORDERS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(order, f, ensure_ascii=False, indent=2)

def delete_order(order_id):
    """删除订单"""
    filename = f"order_{order_id}.json"
    filepath = os.path.join(ORDERS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

@app.route('/images/<filename>')
def uploaded_file(filename):
    """提供上传的图片文件"""
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)

@app.route('/')
def index():
    """主页 - 选择进入厨师端或客户端"""
    return render_template('index.html')

@app.route('/chef')
def chef():
    """厨师端主页"""
    dishes = load_dishes()
    orders = load_orders()
    user_data = load_user_data()
    questionnaire_responses = load_all_questionnaire_responses()
    return render_template('chef.html', 
                         dishes=dishes, 
                         orders=orders,
                         user_balance=user_data['balance'],
                         questionnaire_responses=questionnaire_responses)

@app.route('/update_balance', methods=['POST'])
def update_balance():
    """更新用户宝宝币余额"""
    action = request.form.get('action')
    amount = request.form.get('amount', 0)
    
    try:
        amount = int(amount)
        if amount <= 0:
            flash('金额必须大于0', 'error')
            return redirect(url_for('chef'))
    except:
        flash('请输入有效的金额', 'error')
        return redirect(url_for('chef'))
    
    if action == 'add':
        add_transaction(amount, '厨师端充值', 'income')
        flash(f'成功增加 {amount} 宝宝币', 'success')
    elif action == 'subtract':
        success, message = add_transaction(amount, '厨师端扣除', 'expense')
        if success:
            flash(f'成功扣除 {amount} 宝宝币', 'success')
        else:
            flash(message, 'error')
    else:
        flash('无效的操作', 'error')
    
    return redirect(url_for('chef'))

@app.route('/reset_questionnaire', methods=['POST'])
def reset_questionnaire():
    """重置每日问卷状态"""
    try:
        user_data = load_user_data()
        today = date.today().isoformat()
        
        # 重置今日问卷完成状态
        if today in user_data['daily_questionnaire_completed']:
            del user_data['daily_questionnaire_completed'][today]
            save_user_data(user_data)
            return jsonify({'success': True, 'message': '问卷状态已重置'})
        else:
            return jsonify({'success': False, 'message': '今日问卷尚未完成，无需重置'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'重置失败: {str(e)}'})

@app.route('/customer')
def customer():
    """客户端主页"""
    dishes = load_dishes()
    user_data = load_user_data()
    return render_template('customer.html', 
                         dishes=dishes, 
                         user_data=user_data,
                         balance=user_data['balance'],
                         transactions=user_data['transactions'][:10])  # 显示最近10条交易

@app.route('/customer/<customer_id>')
def customer_with_id(customer_id):
    """带有客户ID的客户端（用于分享链接）"""
    dishes = load_dishes()
    user_data = load_user_data()
    return render_template('customer.html', 
                         dishes=dishes, 
                         customer_id=customer_id,
                         user_data=user_data,
                         balance=user_data['balance'],
                         transactions=user_data['transactions'][:10])

@app.route('/daily_tasks')
def daily_tasks():
    """每日任务页面"""
    user_data = load_user_data()
    questionnaire_completed = is_questionnaire_completed_today()
    return render_template('daily_tasks.html', 
                         balance=user_data['balance'],
                         questionnaire_completed=questionnaire_completed)

@app.route('/farm')
def farm():
    """农场主页面"""
    user_data = check_crop_status()  # 检查作物状态
    seeds_data = load_seeds_data()
    
    return render_template('farm.html', 
                         balance=user_data['balance'],
                         farm_data=user_data['farm'],
                         seeds=seeds_data['seeds'])

@app.route('/buy_seed', methods=['POST'])
def buy_seed():
    """购买种子"""
    data = request.get_json()
    seed_id = data.get('seed_id')
    quantity = data.get('quantity', 1)
    
    user_data = load_user_data()
    seeds_data = load_seeds_data()
    
    if seed_id not in seeds_data['seeds']:
        return jsonify({'success': False, 'message': '种子不存在'})
    
    seed_info = seeds_data['seeds'][seed_id]
    if not seed_info.get('available', True):
        return jsonify({'success': False, 'message': '该种子暂不可购买'})
    
    total_cost = seed_info['price'] * quantity
    
    if user_data['balance'] < total_cost:
        return jsonify({'success': False, 'message': f'宝宝币不足！需要{total_cost}个宝宝币'})
    
    # 扣除宝宝币
    success, message = add_transaction(total_cost, f'购买{seed_info["name"]} x{quantity}', 'expense')
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # 添加种子到库存
    user_data = load_user_data()
    if seed_id not in user_data['farm']['seeds_inventory']:
        user_data['farm']['seeds_inventory'][seed_id] = 0
    user_data['farm']['seeds_inventory'][seed_id] += quantity
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': f'成功购买{seed_info["name"]} x{quantity}',
        'new_balance': user_data['balance'],
        'seeds_inventory': user_data['farm']['seeds_inventory']
    })

@app.route('/buy_fertilizer', methods=['POST'])
def buy_fertilizer():
    """购买粪便"""
    data = request.get_json()
    quantity = data.get('quantity', 1)
    
    user_data = load_user_data()
    price_per_fertilizer = 88
    total_cost = price_per_fertilizer * quantity
    
    if user_data['balance'] < total_cost:
        return jsonify({'success': False, 'message': f'宝宝币不足！需要{total_cost}个宝宝币'})
    
    # 扣除宝宝币
    success, message = add_transaction(total_cost, f'购买粪便 x{quantity}', 'expense')
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # 添加粪便到农场
    user_data = load_user_data()
    user_data['farm']['fertilizer'] += quantity
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': f'成功购买粪便 x{quantity}',
        'new_balance': user_data['balance'],
        'fertilizer': user_data['farm']['fertilizer']
    })

@app.route('/plant_seed', methods=['POST'])
def plant_seed():
    """播种"""
    data = request.get_json()
    seed_id = data.get('seed_id')
    slot_index = data.get('slot_index')
    
    user_data = load_user_data()
    seeds_data = load_seeds_data()
    
    if seed_id not in seeds_data['seeds']:
        return jsonify({'success': False, 'message': '种子不存在'})
    
    if seed_id not in user_data['farm']['seeds_inventory'] or user_data['farm']['seeds_inventory'][seed_id] <= 0:
        return jsonify({'success': False, 'message': '种子库存不足'})
    
    # 检查种植位是否可用
    if slot_index < 0 or slot_index >= user_data['farm']['farm_slots']:
        return jsonify({'success': False, 'message': '种植位无效'})
    
    # 检查该位置是否已被占用
    for crop in user_data['farm']['planted_crops']:
        if crop.get('slot_index') == slot_index and crop['status'] != 'dead':
            return jsonify({'success': False, 'message': '该位置已有作物'})
    
    # 扣除种子库存
    user_data['farm']['seeds_inventory'][seed_id] -= 1
    if user_data['farm']['seeds_inventory'][seed_id] == 0:
        del user_data['farm']['seeds_inventory'][seed_id]
    
    # 添加种植记录
    crop_id = str(uuid.uuid4())[:8]
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    new_crop = {
        'id': crop_id,
        'seed_id': seed_id,
        'slot_index': slot_index,
        'planted_date': current_date,
        'last_watered': None,
        'water_count': 0,
        'fertilizer_count': 0,
        'status': 'growing'
    }
    
    user_data['farm']['planted_crops'].append(new_crop)
    save_user_data(user_data)
    
    seed_info = seeds_data['seeds'][seed_id]
    return jsonify({
        'success': True,
        'message': f'成功播种{seed_info["name"]}',
        'crop': new_crop,
        'seeds_inventory': user_data['farm']['seeds_inventory']
    })

@app.route('/water_crop', methods=['POST'])
def water_crop():
    """浇水"""
    data = request.get_json()
    crop_id = data.get('crop_id')
    
    user_data = load_user_data()
    seeds_data = load_seeds_data()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 检查宝宝币是否足够
    if user_data['balance'] < 52:
        return jsonify({'success': False, 'message': '宝宝币不足！浇水需要52个宝宝币'})
    
    # 找到对应的作物
    crop = None
    for c in user_data['farm']['planted_crops']:
        if c['id'] == crop_id:
            crop = c
            break
    
    if not crop:
        return jsonify({'success': False, 'message': '作物不存在'})
    
    if crop['status'] != 'growing':
        return jsonify({'success': False, 'message': '该作物无法浇水'})
    
    # 检查今日是否已经浇水
    if 'last_watered' in crop and crop['last_watered'] == current_date:
        return jsonify({'success': False, 'message': '今天已经浇过水了！每天只能浇水一次'})
    
    # 扣除宝宝币
    success, message = add_transaction(52, f'浇水({seeds_data["seeds"][crop["seed_id"]]["name"]})', 'expense')
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # 更新作物状态
    user_data = load_user_data()
    
    for c in user_data['farm']['planted_crops']:
        if c['id'] == crop_id:
            c['water_count'] += 1
            c['last_watered'] = current_date
            
            # 检查是否成熟（需要同时满足浇水和施肥要求）
            seed_info = seeds_data['seeds'][c['seed_id']]
            fertilizer_count = c.get('fertilizer_count', 0)
            water_met = c['water_count'] >= seed_info['required_water_count']
            fertilizer_met = fertilizer_count >= seed_info.get('required_fertilizer_count', 0)
            
            if water_met and fertilizer_met:
                c['status'] = 'mature'
            
            crop = c
            break
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': '浇水成功' + ('，作物已成熟！' if crop['status'] == 'mature' else ''),
        'new_balance': user_data['balance'],
        'crop': crop
    })

@app.route('/fertilize_crop', methods=['POST'])
def fertilize_crop():
    """施肥"""
    data = request.get_json()
    crop_id = data.get('crop_id')
    
    user_data = load_user_data()
    seeds_data = load_seeds_data()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 检查粪便是否足够
    if user_data['farm'].get('fertilizer', 0) < 1:
        return jsonify({'success': False, 'message': '粪便不足！施肥需要1个粪便'})
    
    # 找到对应的作物
    crop = None
    for c in user_data['farm']['planted_crops']:
        if c['id'] == crop_id:
            crop = c
            break
    
    if not crop:
        return jsonify({'success': False, 'message': '作物不存在'})
    
    if crop['status'] != 'growing':
        return jsonify({'success': False, 'message': '该作物无法施肥'})
    
    # 检查今日是否已经施肥
    if 'last_fertilized' in crop and crop['last_fertilized'] == current_date:
        return jsonify({'success': False, 'message': '今天已经施过肥了！每天只能施肥一次'})
    
    # 扣除粪便
    user_data['farm']['fertilizer'] -= 1
    
    # 更新作物状态
    for c in user_data['farm']['planted_crops']:
        if c['id'] == crop_id:
            # 为现有作物添加fertilizer_count字段（如果没有的话）
            if 'fertilizer_count' not in c:
                c['fertilizer_count'] = 0
            c['fertilizer_count'] += 1
            c['last_fertilized'] = current_date
            
            # 检查是否成熟（需要同时满足浇水和施肥要求）
            seed_info = seeds_data['seeds'][c['seed_id']]
            water_met = c['water_count'] >= seed_info['required_water_count']
            fertilizer_met = c['fertilizer_count'] >= seed_info.get('required_fertilizer_count', 0)
            
            if water_met and fertilizer_met:
                c['status'] = 'mature'
            
            crop = c
            break
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': '施肥成功' + ('，作物已成熟！' if crop['status'] == 'mature' else ''),
        'fertilizer': user_data['farm']['fertilizer'],
        'crop': crop
    })

@app.route('/harvest_crop', methods=['POST'])
def harvest_crop():
    """收获作物"""
    data = request.get_json()
    crop_id = data.get('crop_id')
    
    user_data = load_user_data()
    seeds_data = load_seeds_data()
    
    # 找到对应的作物
    crop = None
    crop_index = -1
    for i, c in enumerate(user_data['farm']['planted_crops']):
        if c['id'] == crop_id:
            crop = c
            crop_index = i
            break
    
    if not crop:
        return jsonify({'success': False, 'message': '作物不存在'})
    
    if crop['status'] != 'mature':
        return jsonify({'success': False, 'message': '作物尚未成熟'})
    
    # 获取收获物品信息
    seed_info = seeds_data['seeds'][crop['seed_id']]
    harvest_item = seed_info['harvest_item']
    
    # 添加到背包作为实际物品
    user_data['inventory'].append({
        'type': 'physical',
        'name': harvest_item['name'],
        'description': harvest_item['description'],
        'category': 'real_item',
        'quantity': 1,
        'source': f'农场收获({seed_info["name"]})',
        'harvest_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'obtained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # 移除作物
    user_data['farm']['planted_crops'].pop(crop_index)
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': f'收获成功！获得{harvest_item["name"]}',
        'harvested_item': harvest_item
    })

@app.route('/shovel_crop', methods=['POST'])
def shovel_crop():
    """铁铲铲除作物"""
    data = request.get_json()
    crop_id = data.get('crop_id')
    
    user_data = load_user_data()
    
    # 找到对应的作物
    crop_index = -1
    crop = None
    for i, c in enumerate(user_data['farm']['planted_crops']):
        if c['id'] == crop_id:
            crop = c
            crop_index = i
            break
    
    if crop_index == -1:
        return jsonify({'success': False, 'message': '作物不存在'})
    
    # 只能铲除正在生长中的作物，不能铲除成熟的作物
    if crop['status'] == 'mature':
        return jsonify({'success': False, 'message': '成熟的作物不能铲除，请先收获！'})
    
    if crop['status'] == 'dead':
        return jsonify({'success': False, 'message': '请使用清理功能清理死亡作物'})
    
    # 铲除作物
    user_data['farm']['planted_crops'].pop(crop_index)
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': '作物已被铲除'
    })

@app.route('/remove_dead_crop', methods=['POST'])
def remove_dead_crop():
    """移除死亡作物"""
    data = request.get_json()
    crop_id = data.get('crop_id')
    
    user_data = load_user_data()
    
    # 找到对应的作物
    crop_index = -1
    for i, c in enumerate(user_data['farm']['planted_crops']):
        if c['id'] == crop_id:
            if c['status'] == 'dead':
                crop_index = i
                break
    
    if crop_index == -1:
        return jsonify({'success': False, 'message': '作物不存在或状态异常'})
    
    # 移除死亡作物
    user_data['farm']['planted_crops'].pop(crop_index)
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': '死亡作物已清理'
    })

@app.route('/farm_poop', methods=['POST'])
def farm_poop():
    """农场打卡获取粪便"""
    user_data = load_user_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查是否是新的一天，重置打卡次数
    if user_data['farm'].get('last_poop_date') != today:
        user_data['farm']['daily_poop_count'] = 0
        user_data['farm']['last_poop_date'] = today
    
    # 检查当日打卡次数
    poop_count = user_data['farm'].get('daily_poop_count', 0)
    
    if poop_count >= 3:
        return jsonify({
            'success': False, 
            'message': '不给拉了，拉肚子的不能施肥哦'
        })
    
    # 增加打卡次数和粪便数量
    user_data['farm']['daily_poop_count'] += 1
    user_data['farm']['fertilizer'] += 1
    
    # 根据打卡次数返回不同的提示
    messages = [
        '好拉！',
        '两连拉？',
        '拉肚子了？'
    ]
    
    message = messages[poop_count]
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': message,
        'fertilizer': user_data['farm']['fertilizer'],
        'daily_poop_count': user_data['farm']['daily_poop_count']
    })

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    """每日问卷"""
    if is_questionnaire_completed_today():
        flash('今天的问卷已经完成了，明天再来吧！', 'info')
        return redirect(url_for('daily_tasks'))
    
    if request.method == 'POST':
        return process_questionnaire()
    
    user_data = load_user_data()
    return render_template('questionnaire.html', balance=user_data['balance'])

def calculate_consecutive_reward(question_type, current_streak, answer):
    """计算连续答题奖励
    
    Args:
        question_type: 问题类型 ('medicine', 'checkin', 'exercise')
        current_streak: 当前连续天数
        answer: 本次回答 ('有' 或 '没有')
    
    Returns:
        tuple: (新的连续天数, 奖励金额, 奖励描述)
    """
    if answer == '有':
        # 连续回答"有"，增加连续天数并计算奖励
        new_streak = current_streak + 1
        
        if question_type == 'medicine':
            # 按时吃药：基础奖励10币 + 连续天数 * (1-5随机增量)
            base_reward = 10
            streak_bonus = new_streak * random.randint(1, 5)
            reward = base_reward + streak_bonus
            description = f'每日问卷-按时吃药奖励(连续{new_streak}天)'
            
        elif question_type == 'checkin':
            # 小打卡：基础奖励8币 + 连续天数 * 2
            base_reward = 8
            streak_bonus = new_streak * 2
            reward = base_reward + streak_bonus
            description = f'每日问卷-打卡奖励(连续{new_streak}天)'
            
        elif question_type == 'exercise':
            # 健身：基础奖励10币 + 连续天数 * 2
            base_reward = 10
            streak_bonus = new_streak * 2
            reward = base_reward + streak_bonus
            description = f'每日问卷-健身奖励(连续{new_streak}天)'
            
        return new_streak, reward, description
    else:
        # 回答"没有"，重置连续天数
        new_streak = 0
        
        if question_type == 'medicine':
            reward = 1  # 参与奖励
            description = '每日问卷-参与奖励'
        elif question_type == 'checkin':
            reward = 1  # 参与奖励
            description = '每日问卷-参与奖励'
        elif question_type == 'exercise':
            reward = 5  # 健身参与奖励
            description = '每日问卷-健身参与奖励'
            
        return new_streak, reward, description

def process_questionnaire():
    """处理问卷提交"""
    user_data = load_user_data()
    total_reward = 0
    responses = {}
    all_transactions = []  # 收集所有交易
    
    # 问题1：吃药
    medicine = request.form.get('medicine')
    responses['medicine'] = medicine
    new_streak, reward, description = calculate_consecutive_reward('medicine', user_data.get('medicine_streak', 0), medicine)
    user_data['medicine_streak'] = new_streak
    total_reward += reward
    all_transactions.append({
        'amount': reward,
        'description': description,
        'type': 'income'
    })

    # 问题2：打卡
    checkin = request.form.get('checkin')
    responses['checkin'] = checkin
    new_streak, reward, description = calculate_consecutive_reward('checkin', user_data.get('checkin_streak', 0), checkin)
    user_data['checkin_streak'] = new_streak
    total_reward += reward
    all_transactions.append({
        'amount': reward,
        'description': description,
        'type': 'income'
    })
    
    # 问题3：健身
    exercise = request.form.get('exercise')
    responses['exercise'] = exercise
    new_streak, reward, description = calculate_consecutive_reward('exercise', user_data.get('exercise_streak', 0), exercise)
    user_data['exercise_streak'] = new_streak
    total_reward += reward
    all_transactions.append({
        'amount': reward,
        'description': description,
        'type': 'income'
    })
    
    # 问题4：心情 (可选)
    mood = request.form.get('mood', '').strip()
    responses['mood'] = mood
    if mood:
        reward = 15
        total_reward += reward
        all_transactions.append({
            'amount': reward,
            'description': '每日问卷-心情分享奖励',
            'type': 'income'
        })
    
    # 问题5：想说的话 (可选)
    message = request.form.get('message', '').strip()
    responses['message'] = message
    if message:
        reward = 15
        total_reward += reward
        all_transactions.append({
            'amount': reward,
            'description': '每日问卷-留言奖励',
            'type': 'income'
        })
    
    # 问题6：乐观
    optimism = request.form.get('optimism')
    responses['optimism'] = optimism
    if optimism == '有':
        user_data['optimism_streak'] += 1
        reward = 5 + user_data['optimism_streak']
        total_reward += reward
        all_transactions.append({
            'amount': reward,
            'description': f'每日问卷-乐观奖励(连续{user_data["optimism_streak"]}天)',
            'type': 'income'
        })
    else:
        user_data['optimism_streak'] = 0
        reward = 1
        total_reward += reward
        all_transactions.append({
            'amount': reward,
            'description': '每日问卷-参与奖励',
            'type': 'income'
        })
    
    # 问题7：随机奖励 (从前端获取)
    random_reward = request.form.get('random_reward')
    if random_reward:
        random_reward = int(random_reward)
        total_reward += random_reward
        responses['random_reward'] = random_reward
        all_transactions.append({
            'amount': random_reward,
            'description': '每日问卷-随机奖励',
            'type': 'income'
        })
    else:
        # 如果没有随机奖励（防御性编程），使用默认值
        random_reward = 1
        total_reward += random_reward
        responses['random_reward'] = random_reward
        all_transactions.append({
            'amount': random_reward,
            'description': '每日问卷-默认奖励',
            'type': 'income'
        })
    
    # 一次性更新用户余额和添加所有交易记录
    user_data['balance'] += total_reward
    
    # 添加所有交易记录
    for trans_data in all_transactions:
        transaction = {
            'id': str(uuid.uuid4())[:8],
            'amount': trans_data['amount'],
            'description': trans_data['description'],
            'type': trans_data['type'],
            'timestamp': int(datetime.now().timestamp()),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        user_data['transactions'].insert(0, transaction)
    
    # 保存更新后的用户数据
    save_user_data(user_data)
    
    # 保存问卷回答
    responses['total_reward'] = total_reward
    save_questionnaire_response(responses)
    
    # 标记问卷已完成
    mark_questionnaire_completed()
    
    flash(f'问卷完成！获得 {total_reward} 宝宝币奖励！余额已更新为 {user_data["balance"]} 宝宝币', 'success')
    return redirect(url_for('daily_tasks'))

@app.route('/check_in_page')
def check_in_page():
    """签到页面"""
    user_data = load_user_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查今天是否已签到
    can_check_in = today not in user_data['check_in_history']
    
    # 生成当月日历数据
    now = datetime.now()
    current_month = now.strftime('%Y年%m月')
    
    # 获取当月第一天和最后一天
    first_day = datetime(now.year, now.month, 1)
    if now.month == 12:
        last_day = datetime(now.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
    
    # 生成日历周数据
    calendar_weeks = []
    current_date = first_day - timedelta(days=first_day.weekday() + 1)  # 从周日开始
    if current_date.weekday() != 6:  # 如果不是周日，调整到上个周日
        current_date = current_date - timedelta(days=(current_date.weekday() + 1) % 7)
    
    # 生成6周的日历数据
    for week in range(6):
        week_days = []
        for day in range(7):
            date_str = current_date.strftime('%Y-%m-%d')
            is_current_month = current_date.month == now.month
            is_today = date_str == today
            is_future = current_date > now
            checked_in = date_str in user_data['check_in_history']
            
            day_data = {
                'day': current_date.day,
                'date': date_str,
                'is_current_month': is_current_month,
                'is_today': is_today,
                'is_future': is_future,
                'checked_in': checked_in,
                'reward': user_data['check_in_history'].get(date_str, 0) if checked_in else 0
            }
            week_days.append(day_data)
            current_date += timedelta(days=1)
        
        calendar_weeks.append(week_days)
        # 如果本周包含了下个月的日期，停止生成
        if current_date.month != now.month and any(day['is_current_month'] for day in week_days):
            break
    
    # 计算可用优惠券数量
    available_coupons = sum(1 for coupon in user_data['coupons'] if not coupon.get('used', False))
    
    return render_template('check_in.html',
                         balance=user_data['balance'],
                         consecutive_days=user_data['consecutive_days'],
                         total_check_ins=len(user_data['check_in_history']),
                         available_coupons=available_coupons,
                         can_check_in=can_check_in,
                         current_month=current_month,
                         calendar_weeks=calendar_weeks,
                         user_coupons=user_data['coupons'])

@app.route('/check_in', methods=['POST'])
def check_in():
    """处理签到请求"""
    user_data = load_user_data()
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 检查今天是否已签到
    if today in user_data['check_in_history']:
        return jsonify({'success': False, 'message': '今天已经签到过了'})
    
    # 计算签到奖励
    if len(user_data['check_in_history']) == 0:
        # 首次签到
        reward = 5
        user_data['consecutive_days'] = 1
    else:
        # 检查连续签到
        if yesterday in user_data['check_in_history']:
            # 连续签到：在上一天基础上额外随机增加5-10个币
            yesterday_reward = user_data['check_in_history'][yesterday]
            extra_reward = random.randint(5, 10)
            reward = yesterday_reward + extra_reward
            user_data['consecutive_days'] += 1
        else:
            # 不连续签到：重新开始计算
            reward = 5
            user_data['consecutive_days'] = 1
    
    # 记录签到
    user_data['check_in_history'][today] = reward
    user_data['total_check_ins'] = len(user_data['check_in_history'])
    
    # 添加宝宝币奖励
    user_data['balance'] += reward
    
    # 添加交易记录
    transaction = {
        'id': str(uuid.uuid4())[:8],
        'amount': reward,
        'description': f'每日签到奖励(连续{user_data["consecutive_days"]}天)',
        'type': 'income',
        'timestamp': int(datetime.now().timestamp()),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    user_data['transactions'].insert(0, transaction)
    
    # 检查连续签到奖励
    bonus_reward = False
    bonus_message = ""
    
    if user_data['consecutive_days'] == 7:
        # 连续7天奖励9折券
        coupon = {
            'id': str(uuid.uuid4())[:8],
            'type': 'discount',
            'value': 0.9,
            'description': '连续签到7天奖励',
            'expires': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'used': False,
            'created_date': today
        }
        user_data['coupons'].append(coupon)
        bonus_reward = True
        bonus_message = "恭喜获得9折优惠券！"
        
    elif user_data['consecutive_days'] == 30:
        # 连续30天奖励免单券
        coupon = {
            'id': str(uuid.uuid4())[:8],
            'type': 'free',
            'value': 1,
            'description': '连续签到30天奖励',
            'expires': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'used': False,
            'created_date': today
        }
        user_data['coupons'].append(coupon)
        bonus_reward = True
        bonus_message = "恭喜获得免单券！"
    
    # 保存用户数据
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'reward': reward,
        'consecutive_days': user_data['consecutive_days'],
        'bonus_reward': bonus_reward,
        'bonus_message': bonus_message
    })

@app.route('/make_up_check_in', methods=['POST'])
def make_up_check_in():
    """补签功能"""
    data = request.get_json()
    target_date = data.get('date')
    
    user_data = load_user_data()
    
    # 检查是否有补签卡
    if user_data.get('make_up_cards', 0) <= 0:
        return jsonify({'success': False, 'message': '没有补签卡'})
    
    # 检查目标日期
    if not target_date:
        return jsonify({'success': False, 'message': '请选择补签日期'})
    
    # 检查该日期是否已签到
    if target_date in user_data['check_in_history']:
        return jsonify({'success': False, 'message': '该日期已经签到过了'})
    
    # 检查日期是否在合理范围内（不能补签未来的日期）
    target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
    if target_datetime > datetime.now():
        return jsonify({'success': False, 'message': '不能补签未来的日期'})
    
    # 使用补签卡
    user_data['make_up_cards'] -= 1
    
    # 计算补签奖励（固定5个宝宝币）
    reward = 5
    user_data['check_in_history'][target_date] = reward
    user_data['balance'] += reward
    
    # 添加交易记录
    transaction = {
        'id': str(uuid.uuid4())[:8],
        'amount': reward,
        'description': f'补签奖励({target_date})',
        'type': 'income',
        'timestamp': int(datetime.now().timestamp()),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    user_data['transactions'].insert(0, transaction)
    
    # 更新背包中的补签卡数量
    for item in user_data.get('inventory', []):
        if item['name'] == '补签卡' and item['category'] == 'check_in_item':
            item['quantity'] = user_data['make_up_cards']
            if item['quantity'] <= 0:
                user_data['inventory'].remove(item)
            break
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'reward': reward,
        'remaining_cards': user_data['make_up_cards'],
        'new_balance': user_data['balance']
    })

@app.route('/guess_game')
def guess_game():
    """猜数字游戏页面"""
    user_data = load_user_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 重置每日游戏次数（如果是新的一天）
    last_game_date = user_data.get('last_game_date', '')
    if last_game_date != today:
        user_data['daily_guess_games'] = 0
        user_data['last_game_date'] = today
        save_user_data(user_data)
    
    # 统一使用daily_guess_games字段
    games_played = user_data.get('daily_guess_games', 0)
    extra_chances = user_data.get('extra_game_chances', 0)
    total_available = 10 + extra_chances
    games_remaining = max(0, total_available - games_played)
    
    print(f"DEBUG: games_played={games_played}, extra_chances={extra_chances}, total_available={total_available}, games_remaining={games_remaining}")
    
    return render_template('guess_game.html',
                         balance=user_data['balance'],
                         games_played=games_played,
                         games_remaining=games_remaining,
                         extra_chances=extra_chances)

@app.route('/start_guess_game', methods=['POST'])
def start_guess_game():
    """开始新的猜数字游戏"""
    user_data = load_user_data()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查今日游戏次数
    games_played = user_data.get('daily_guess_games', 0)
    extra_chances = user_data.get('extra_game_chances', 0)
    total_available = 10 + extra_chances
    
    print(f"DEBUG start_guess_game: games_played={games_played}, extra_chances={extra_chances}, total_available={total_available}")
    
    if games_played >= total_available:
        return jsonify({'success': False, 'message': '今日游戏次数已用完'})
    
    # 生成随机数字和游戏ID
    target_number = random.randint(1, 52)
    game_id = str(uuid.uuid4())[:8]
    
    # 在会话中存储当前游戏信息
    session['current_guess_game'] = {
        'id': game_id,
        'target_number': target_number,
        'attempts_used': 0,
        'started_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'target_number': target_number  # 实际部署时应该移除这个，这里仅用于测试
    })

@app.route('/make_guess', methods=['POST'])
def make_guess():
    """处理用户猜测"""
    data = request.get_json()
    game_id = data.get('game_id')
    guess = data.get('guess')
    
    if not guess or guess < 1 or guess > 52:
        return jsonify({'success': False, 'message': '请输入1-52之间的数字'})
    
    # 验证游戏会话
    current_game = session.get('current_guess_game')
    if not current_game or current_game['id'] != game_id:
        return jsonify({'success': False, 'message': '游戏会话无效，请重新开始'})
    
    target_number = current_game['target_number']
    old_attempts = current_game['attempts_used']
    attempts_used = current_game['attempts_used'] + 1
    
    # 调试信息 - 追踪session状态
    print(f"DEBUG: Before update - old_attempts={old_attempts}, new_attempts={attempts_used}")
    print(f"DEBUG: Session game_id={current_game['id']}, request_game_id={game_id}")
    
    # 更新尝试次数
    session['current_guess_game']['attempts_used'] = attempts_used
    session.modified = True  # 显式标记session为已修改
    print(f"DEBUG: After session update - attempts_used={session['current_guess_game']['attempts_used']}")
    
    result = ''
    hint = ''
    reward = 0
    
    if guess == target_number:
        # 猜中了
        result = 'correct'
        hint = f'恭喜！正确答案就是 {target_number}！'
        
        # 计算奖励 - 新的7次机会奖励规则
        reward_map = {1: 520, 2: 100, 3: 52, 4: 52, 5: 52, 6: 25, 7: 25}
        reward = reward_map.get(attempts_used, 25)  # 默认25宝宝币
        
        # 调试信息 - 可以在部署时移除
        print(f"DEBUG: attempts_used={attempts_used}, reward={reward}")
        
        # 更新用户数据
        user_data = load_user_data()
        user_data['balance'] += reward
        user_data['daily_guess_games'] = user_data.get('daily_guess_games', 0) + 1
        
        # 如果超过了基础10次游戏，扣除额外机会
        games_after_update = user_data['daily_guess_games']
        if games_after_update > 10:
            extra_chances = user_data.get('extra_game_chances', 0)
            if extra_chances > 0:
                user_data['extra_game_chances'] -= 1
                print(f"DEBUG: Used extra chance, remaining: {user_data['extra_game_chances']}")
        
        # 更新游戏历史
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in user_data.get('guess_game_history', {}):
            user_data['guess_game_history'][today] = {'games_played': 0, 'total_reward': 0}
        
        user_data['guess_game_history'][today]['games_played'] += 1
        user_data['guess_game_history'][today]['total_reward'] += reward
        
        # 添加交易记录
        transaction = {
            'id': str(uuid.uuid4())[:8],
            'amount': reward,
            'description': f'猜数字游戏奖励(第{attempts_used}次猜中)',
            'type': 'income',
            'timestamp': int(datetime.now().timestamp()),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        user_data['transactions'].insert(0, transaction)
        
        save_user_data(user_data)
        
        # 清除游戏会话
        session.pop('current_guess_game', None)
        
        return jsonify({
            'success': True,
            'result': result,
            'hint': hint,
            'reward': reward,
            'new_balance': user_data['balance'],
            'attempts_used': attempts_used
        })
    
    elif guess > target_number:
        result = 'too_high'
        hint = f'{guess} 太大了，再试试小一点的数字'
    else:
        result = 'too_low'
        hint = f'{guess} 太小了，再试试大一点的数字'
    
    # 检查是否用完所有机会
    if attempts_used >= 7:  # 更新为7次机会
        # 游戏结束，更新游戏次数但不给奖励
        user_data = load_user_data()
        user_data['daily_guess_games'] = user_data.get('daily_guess_games', 0) + 1
        
        # 如果超过了基础10次游戏，扣除额外机会
        games_after_update = user_data['daily_guess_games']
        if games_after_update > 10:
            extra_chances = user_data.get('extra_game_chances', 0)
            if extra_chances > 0:
                user_data['extra_game_chances'] -= 1
                print(f"DEBUG: Used extra chance (failed game), remaining: {user_data['extra_game_chances']}")
        
        save_user_data(user_data)
        
        # 清除游戏会话
        session.pop('current_guess_game', None)
        
        return jsonify({
            'success': True,
            'result': 'failed',
            'hint': f'很遗憾，正确答案是 {target_number}',
            'correct_number': target_number,
            'attempts_used': attempts_used
        })
    
    return jsonify({
        'success': True,
        'result': result,
        'hint': hint,
        'attempts_used': attempts_used
    })

@app.route('/buy_game_chance', methods=['POST'])
def buy_game_chance():
    """购买游戏机会"""
    user_data = load_user_data()
    
    # 检查余额
    if user_data['balance'] < 52:
        return jsonify({'success': False, 'message': '宝宝币不足！需要52个宝宝币。'})
    
    # 扣除宝宝币
    success, message = add_transaction(52, '购买游戏机会', 'expense')
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # 增加额外游戏机会
    user_data = load_user_data()
    if 'extra_game_chances' not in user_data:
        user_data['extra_game_chances'] = 0
    user_data['extra_game_chances'] += 1
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': '购买成功！获得1次额外游戏机会。',
        'new_balance': user_data['balance'],
        'extra_chances': user_data['extra_game_chances']
    })

def calculate_random_reward():
    """计算随机奖励"""
    rand = random.random() * 100
    
    if rand < 0.52:  # 0.52%
        return 520
    elif rand < 2:   # 2% - 0.52% = 1.48%
        return 52
    elif rand < 5:   # 5% - 2% = 3%
        return 40
    elif rand < 10:  # 10% - 5% = 5%
        return random.randint(30, 39)
    elif rand < 15:  # 15% - 10% = 5%
        return random.randint(20, 29)
    else:           # 85%
        return random.randint(1, 19)

@app.route('/add_dish', methods=['POST'])
def add_dish():
    """添加新菜品"""
    dish_name = request.form.get('dish_name', '').strip()
    dish_price = request.form.get('dish_price', '52')
    
    if not dish_name:
        flash('请输入菜品名称', 'error')
        return redirect(url_for('chef'))
    
    try:
        dish_price = int(dish_price)
        if dish_price < 0:
            dish_price = 52
    except:
        dish_price = 52
    
    # 处理上传的图片
    if 'dish_image' not in request.files:
        flash('请选择菜品图片', 'error')
        return redirect(url_for('chef'))
    
    file = request.files['dish_image']
    if file.filename == '':
        flash('请选择菜品图片', 'error')
        return redirect(url_for('chef'))
    
    if file and allowed_file(file.filename):
        try:
            # 生成唯一文件名
            timestamp = int(datetime.now().timestamp())
            random_str = str(uuid.uuid4())[:8]
            file_ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
            filename = f"dish_{timestamp}_{random_str}.{file_ext}"
            
            # 保存文件
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 处理图片
            img = Image.open(file.stream)
            if img.mode in ('RGBA', 'LA', 'P'):
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存处理后的图片
            img.save(filepath, 'JPEG', quality=95)
            
            # 添加到菜品列表
            dishes = load_dishes()
            new_dish = {
                'name': dish_name,
                'price': dish_price,
                'image_path': f'images/{filename}'
            }
            dishes.append(new_dish)
            save_dishes(dishes)
            
            flash(f'菜品 "{dish_name}" 添加成功！价格：{dish_price}宝宝币', 'success')
            
        except Exception as e:
            flash(f'添加菜品失败: {str(e)}', 'error')
    else:
        flash('不支持的图片格式，请选择 PNG、JPG、JPEG、GIF 或 BMP 格式', 'error')
    
    return redirect(url_for('chef'))

@app.route('/batch_add_dishes', methods=['POST'])
def batch_add_dishes():
    """批量添加菜品"""
    dish_names = request.form.getlist('dish_names[]')
    dish_prices = request.form.getlist('dish_prices[]')
    dish_images = request.files.getlist('dish_images[]')
    
    if not dish_names or not dish_images:
        flash('请填写菜品信息', 'error')
        return redirect(url_for('chef'))
    
    if len(dish_names) != len(dish_images):
        flash('菜品名称和图片数量不匹配', 'error')
        return redirect(url_for('chef'))
    
    # 如果价格数量不匹配，用默认价格52填充
    if len(dish_prices) != len(dish_names):
        dish_prices = ['52'] * len(dish_names)
    
    success_count = 0
    error_count = 0
    error_messages = []
    
    dishes = load_dishes()
    
    for i, (dish_name, dish_price, file) in enumerate(zip(dish_names, dish_prices, dish_images)):
        dish_name = dish_name.strip()
        
        # 处理价格
        try:
            dish_price = int(dish_price) if dish_price else 52
            if dish_price < 0:
                dish_price = 52
        except:
            dish_price = 52
        
        # 验证菜品名称
        if not dish_name:
            error_count += 1
            error_messages.append(f'第 {i+1} 道菜品名称不能为空')
            continue
        
        # 验证图片文件
        if file.filename == '':
            error_count += 1
            error_messages.append(f'第 {i+1} 道菜品 "{dish_name}" 未选择图片')
            continue
        
        if not allowed_file(file.filename):
            error_count += 1
            error_messages.append(f'第 {i+1} 道菜品 "{dish_name}" 的图片格式不支持')
            continue
        
        try:
            # 生成唯一文件名
            timestamp = int(datetime.now().timestamp())
            random_str = str(uuid.uuid4())[:8]
            file_ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
            filename = f"dish_{timestamp}_{random_str}_{i}.{file_ext}"
            
            # 保存文件
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 处理图片
            img = Image.open(file.stream)
            if img.mode in ('RGBA', 'LA', 'P'):
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存处理后的图片
            img.save(filepath, 'JPEG', quality=95)
            
            # 添加到菜品列表
            new_dish = {
                'name': dish_name,
                'price': dish_price,
                'image_path': f'images/{filename}'
            }
            dishes.append(new_dish)
            success_count += 1
            
        except Exception as e:
            error_count += 1
            error_messages.append(f'第 {i+1} 道菜品 "{dish_name}" 处理失败: {str(e)}')
    
    # 保存所有成功添加的菜品
    if success_count > 0:
        save_dishes(dishes)
    
    # 显示结果消息
    if success_count > 0:
        flash(f'成功添加 {success_count} 道菜品！', 'success')
    
    if error_count > 0:
        flash(f'有 {error_count} 道菜品添加失败', 'error')
        for msg in error_messages:
            flash(msg, 'error')
    
    return redirect(url_for('chef'))

@app.route('/delete_dish', methods=['POST'])
def delete_dish():
    """删除菜品"""
    dish_index = request.form.get('dish_index', type=int)
    
    dishes = load_dishes()
    if 0 <= dish_index < len(dishes):
        deleted_dish = dishes.pop(dish_index)
        save_dishes(dishes)
        flash(f'菜品 "{deleted_dish["name"]}" 已删除', 'success')
    else:
        flash('删除失败：菜品不存在', 'error')
    
    return redirect(url_for('chef'))

@app.route('/place_order', methods=['POST'])
def place_order():
    """客户下单"""
    data = request.get_json()
    customer_name = data.get('customer_name', '宝包用户').strip()
    selected_dishes = data.get('selected_dishes', [])
    customer_id = data.get('customer_id', 'unknown')
    original_cost = data.get('original_cost', 0)
    final_cost = data.get('final_cost', 0)
    discount = data.get('discount', 0)
    coupon_id = data.get('coupon_id')
    
    if not selected_dishes:
        return jsonify({'success': False, 'message': '请选择菜品'})
    
    if not customer_name:
        customer_name = '宝包用户'
    
    # 验证计算是否正确
    dishes = load_dishes()
    dish_prices = {dish['name']: dish.get('price', 52) for dish in dishes}
    
    calculated_cost = 0
    order_details = []
    dish_counts = {}
    
    for dish_name in selected_dishes:
        dish_counts[dish_name] = dish_counts.get(dish_name, 0) + 1
    
    for dish_name, count in dish_counts.items():
        price = dish_prices.get(dish_name, 52)
        subtotal = price * count
        calculated_cost += subtotal
        order_details.append({
            'name': dish_name,
            'price': price,
            'count': count,
            'subtotal': subtotal
        })
    
    # 验证原始费用
    if calculated_cost != original_cost:
        return jsonify({'success': False, 'message': '订单金额计算错误，请刷新重试'})
    
    # 处理优惠券
    user_data = load_user_data()
    discount_applied = 0
    used_coupon = None
    
    if coupon_id:
        # 查找优惠券
        coupon = None
        for c in user_data['coupons']:
            if c['id'] == coupon_id:
                coupon = c
                break
        
        if not coupon:
            return jsonify({'success': False, 'message': '优惠券不存在'})
        
        if coupon.get('used', False):
            return jsonify({'success': False, 'message': '优惠券已被使用'})
        
        # 检查有效期
        if datetime.now() > datetime.strptime(coupon['expires'], '%Y-%m-%d'):
            return jsonify({'success': False, 'message': '优惠券已过期'})
        
        # 计算折扣
        if coupon['type'] == 'free':
            discount_applied = original_cost
            final_cost = 0
        elif coupon['type'] == 'discount':
            discount_applied = original_cost - math.ceil(original_cost * coupon['value'])
            final_cost = original_cost - discount_applied
        
        # 验证最终费用
        if final_cost != data.get('final_cost', 0):
            return jsonify({'success': False, 'message': '优惠券折扣计算错误，请刷新重试'})
        
        used_coupon = coupon
    else:
        final_cost = original_cost
    
    # 检查余额
    if user_data['balance'] < final_cost:
        return jsonify({
            'success': False, 
            'message': f'宝宝币余额不足！需要 {final_cost} 宝宝币，当前余额 {user_data["balance"]} 宝宝币'
        })
    
    # 扣除宝宝币
    transaction_desc = f'购买菜品订单'
    if used_coupon:
        transaction_desc += f'(使用{used_coupon["description"]})'
    
    success, message = add_transaction(final_cost, transaction_desc, 'expense')
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # 标记优惠券为已使用
    if used_coupon:
        # 更新coupons列表中的优惠券状态
        for c in user_data['coupons']:
            if c['id'] == coupon_id:
                c['used'] = True
                c['used_date'] = datetime.now().strftime('%Y-%m-%d')
                break
        
        # 减少库存中对应的优惠券数量
        # 首先尝试通过coupon_id匹配
        inventory_updated = False
        for inv_item in user_data.get('inventory', []):
            if (inv_item.get('type') == 'coupon' and 
                inv_item.get('coupon_id') == coupon_id and 
                inv_item.get('quantity', 0) > 0):
                inv_item['quantity'] -= 1
                if inv_item['quantity'] <= 0:
                    user_data['inventory'].remove(inv_item)
                print(f"DEBUG: Reduced coupon by coupon_id, remaining: {inv_item.get('quantity', 0)}")
                inventory_updated = True
                break
        
        # 如果通过coupon_id没有匹配到，尝试通过优惠券类型和值匹配
        if not inventory_updated:
            for inv_item in user_data.get('inventory', []):
                if inv_item.get('type') == 'coupon' and inv_item.get('quantity', 0) > 0:
                    # 根据优惠券类型和折扣值来匹配库存中的优惠券
                    coupon_name_match = False
                    
                    if used_coupon['type'] == 'discount':
                        if used_coupon['value'] == 0.6 and inv_item.get('name') == '6折优惠券':
                            coupon_name_match = True
                        elif used_coupon['value'] == 0.8 and inv_item.get('name') == '8折优惠券':
                            coupon_name_match = True
                        elif used_coupon['value'] == 0.9 and inv_item.get('name') == '9折优惠券':
                            coupon_name_match = True
                        elif used_coupon['value'] == 0.5 and inv_item.get('name') == '5折优惠券':
                            coupon_name_match = True
                    elif used_coupon['type'] == 'free' and inv_item.get('name') == '免费优惠券':
                        coupon_name_match = True
                    
                    if coupon_name_match:
                        inv_item['quantity'] -= 1
                        if inv_item['quantity'] <= 0:
                            user_data['inventory'].remove(inv_item)
                        print(f"DEBUG: Reduced {inv_item.get('name')} by type match, remaining: {inv_item.get('quantity', 0)}")
                        break
        
        save_user_data(user_data)
    
    # 创建订单
    order_id = str(uuid.uuid4())[:8]
    order = {
        'id': order_id,
        'customer_name': customer_name,
        'customer_id': customer_id,
        'dishes': selected_dishes,
        'order_details': order_details,
        'original_cost': original_cost,
        'final_cost': final_cost,
        'discount_applied': discount_applied,
        'coupon_used': used_coupon['description'] if used_coupon else None,
        'timestamp': int(datetime.now().timestamp()),
        'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending'
    }
    
    try:
        save_order(order)
        response_data = {
            'success': True, 
            'message': f'订单提交成功！', 
            'order_id': order_id,
            'original_cost': original_cost,
            'final_cost': final_cost,
            'total_cost': final_cost,  # 兼容前端
            'new_balance': user_data['balance'] - final_cost
        }
        
        if discount_applied > 0:
            response_data['discount_applied'] = discount_applied
            response_data['message'] += f'使用优惠券节省 {discount_applied} 宝宝币！'
        
        return jsonify(response_data)
    except Exception as e:
        # 如果订单保存失败，退还宝宝币和优惠券
        add_transaction(final_cost, f'订单失败退款-{order_id}', 'income')
        if used_coupon:
            for c in user_data['coupons']:
                if c['id'] == coupon_id:
                    c['used'] = False
                    c.pop('used_date', None)
                    break
            save_user_data(user_data)
        return jsonify({'success': False, 'message': f'订单提交失败: {str(e)}'})

@app.route('/complete_order', methods=['POST'])
def complete_order():
    """完成订单（厨师端）"""
    order_id = request.form.get('order_id')
    
    if delete_order(order_id):
        flash(f'订单 {order_id} 已完成并删除', 'success')
    else:
        flash('删除订单失败', 'error')
    
    return redirect(url_for('chef'))

@app.route('/generate_customer_link', methods=['POST'])
def generate_customer_link():
    """生成客户端链接"""
    customer_id = str(uuid.uuid4())[:8]
    base_url = request.host_url.rstrip('/')
    customer_url = f"{base_url}/customer/{customer_id}"
    
    return jsonify({
        'success': True,
        'customer_id': customer_id,
        'customer_url': customer_url
    })

@app.route('/get_orders')
def get_orders():
    """获取所有订单（用于实时更新）"""
    orders = load_orders()
    return jsonify(orders)

# 碎片合成配置
FRAGMENT_RECIPES = {
    '德湘厨兑换券': {
        'fragments_needed': 10,
        'result_item': {
            'type': 'physical',
            'name': '德湘厨兑换券',
            'description': '德湘厨餐厅兑换券（实际物品）',
            'category': 'real_item'
        }
    },
    '金戈戈': {
        'fragments_needed': 10,
        'result_item': {
            'type': 'physical',
            'name': '金戈戈',
            'description': '金戈戈（实际物品）',
            'category': 'real_item'
        }
    },
    '麦辣鸡腿堡': {
        'fragments_needed': 10,
        'result_item': {
            'type': 'physical',
            'name': '麦辣鸡腿堡',
            'description': '麦辣鸡腿堡（实际物品）',
            'category': 'real_item'
        }
    },
    '奥尔良鸡腿堡': {
        'fragments_needed': 10,
        'result_item': {
            'type': 'physical',
            'name': '奥尔良鸡腿堡',
            'description': '奥尔良鸡腿堡（实际物品）',
            'category': 'real_item'
        }
    },
    '奶茶鼠玩偶': {
        'fragments_needed': 5,
        'result_item': {
            'type': 'physical',
            'name': '奶茶鼠玩偶',
            'description': '奶茶鼠玩偶（实际物品）',
            'category': 'real_item'
        }
    },
    '荒野乱斗乱斗金券🤪': {
        'fragments_needed': 5,
        'result_item': {
            'type': 'physical',
            'name': '荒野乱斗乱斗金券🤪',
            'description': '荒野乱斗乱斗金券🤪（实际物品）',
            'category': 'real_item'
        }
    },
    '星巴克一杯': {
        'fragments_needed': 4,
        'result_item': {
            'type': 'physical',
            'name': '星巴克一杯',
            'description': '星巴克一杯（实际物品）',
            'category': 'real_item'
        }
    },
    '寿司郎': {
        'fragments_needed': 9,
        'result_item': {
            'type': 'physical',
            'name': '寿司郎',
            'description': '寿司郎（实际物品）',
            'category': 'real_item'
        }
    },
    '水牛奶一箱': {
        'fragments_needed': 4,
        'result_item': {
            'type': 'physical',
            'name': '水牛奶一箱',
            'description': '水牛奶一箱（实际物品）',
            'category': 'real_item'
        }
    },
    'switch': {
        'fragments_needed': 11,
        'result_item': {
            'type': 'physical',
            'name': 'Nintendo Switch',
            'description': 'Nintendo Switch游戏机（实际物品）',
            'category': 'real_item'
        }
    }
}

# 抽奖系统
def perform_draw(draw_type, num_draws=1):
    """执行抽奖"""
    results = []
    
    for _ in range(num_draws):
        rand = random.random() * 100
        
        if draw_type == 'normal':
            # 普通抽奖的奖品和概率信息（按新要求）
            if rand < 1.25:
                results.append({'type': 'physical_item', 'name': '面包', 'description': '面包（实际物品）'})
            elif rand < 2.75:
                results.append({'type': 'fragment', 'name': '德湘厨兑换券碎片', 'fragment_type': '德湘厨兑换券', 'description': '德湘厨兑换券碎片（在背包中10个合成一个实际物品才能使用）'})
            elif rand < 4.25:
                results.append({'type': 'fragment', 'name': '金戈戈碎片', 'fragment_type': '金戈戈', 'description': '金戈戈碎片（在背包中10个合成一个实际物品才能使用）'})
            elif rand < 5.5:
                results.append({'type': 'physical_item', 'name': '黑咖啡一杯', 'description': '黑咖啡一杯（实际物品）'})
            elif rand < 8.0:
                results.append({'type': 'fragment', 'name': '麦辣鸡腿堡碎片', 'fragment_type': '麦辣鸡腿堡', 'description': '麦辣鸡腿堡碎片（在背包中10个合成一个实际物品才能使用）'})
            elif rand < 10.5:
                results.append({'type': 'fragment', 'name': '奥尔良鸡腿堡碎片', 'fragment_type': '奥尔良鸡腿堡', 'description': '奥尔良鸡腿堡碎片（在背包中10个合成一个实际物品才能使用）'})
            elif rand < 11.5:
                results.append({'type': 'physical_item', 'name': '奶茶一杯', 'description': '奶茶一杯（实际物品）'})
            elif rand < 12.5:
                results.append({'type': 'physical_item', 'name': '紫菜卷', 'description': '紫菜卷（实际物品）'})
            elif rand < 20.0:
                results.append({'type': 'coupon', 'value': 0.9, 'name': '九折优惠券', 'description': '九折优惠券'})
            elif rand < 60.0:
                results.append({'type': 'balance', 'value': 25, 'name': '宝宝币25个', 'description': '获得25个宝宝币'})
            elif rand < 70.0:
                results.append({'type': 'balance_deduction', 'value': -20, 'name': '扣除20宝宝币', 'description': '扣除20个宝宝币'})
            else:
                results.append({'type': 'balance', 'value': 10, 'name': '宝宝币10枚', 'description': '获得10个宝宝币'})
                
        elif draw_type == 'premium':
            # 高级抽奖的奖品和概率信息（与前端同步，合并芒果/西瓜、香蕉/火龙果）
            if num_draws > 7:
                num_draws = 7
            if rand < 11.25:
                results.append({'type': 'physical_item', 'name': '按摩15分钟', 'description': '按摩15分钟（实际物品）'})
            elif rand < 12.5:
                results.append({'type': 'physical_item', 'name': '番茄成品', 'description': '番茄成品（实际物品）'})
            elif rand < 32.5:
                results.append({'type': 'balance_deduction', 'value': -50, 'name': '扣除50宝宝币', 'description': '扣除50宝宝币'})
            elif rand < 33.75:
                results.append({'type': 'physical_item', 'name': '芒果，西瓜', 'description': '芒果，西瓜（实际物品）'})
            elif rand < 35.0:
                results.append({'type': 'physical_item', 'name': '香蕉，火龙果', 'description': '香蕉，火龙果（实际物品）'})
            elif rand < 35.5:
                results.append({'type': 'physical_item', 'name': '100r衣服兑换券（实际物品）惊喜大礼', 'description': '100r衣服兑换券（实际物品）惊喜大礼'})
            elif rand < 36.75:
                results.append({'type': 'physical_item', 'name': '按摩30分钟', 'description': '按摩30分钟（实际物品）'})
            elif rand < 38.0:
                results.append({'type': 'coupon', 'value': 0.6, 'name': '六折优惠券', 'description': '六折优惠券'})
            elif rand < 39.25:
                results.append({'type': 'coupon', 'value': 1.0, 'name': '免单券', 'description': '免单券'})
            elif rand < 40.5:
                results.append({'type': 'physical_item', 'name': '外卖盲盒', 'description': '外卖盲盒（实际物品）'})
            elif rand < 93.0:
                results.append({'type': 'balance', 'value': 200, 'name': '200个宝宝币', 'description': '获得200个宝宝币'})
            elif rand < 94.0:
                results.append({'type': 'physical_item', 'name': '麦辣鸡腿堡2', 'description': '麦辣鸡腿堡2（实际物品可直接使用）'})
            elif rand < 95.0:
                results.append({'type': 'fragment', 'name': '奶茶鼠玩偶', 'fragment_type': '奶茶鼠玩偶', 'description': '奶茶鼠玩偶（在背包中5个合成一个实际物品才能使用）'})
            elif rand < 96.25:
                results.append({'type': 'fragment', 'name': '荒野乱斗乱斗金券🤪', 'fragment_type': '荒野乱斗乱斗金券🤪', 'description': '荒野乱斗乱斗金券🤪（在背包中5个合成一个实际物品才能使用）'})
            elif rand < 97.5:
                results.append({'type': 'fragment', 'name': '星巴克一杯', 'fragment_type': '星巴克一杯', 'description': '星巴克一杯（在背包中4个合成一个实际物品才能使用）'})
            elif rand < 98.75:
                results.append({'type': 'fragment', 'name': '寿司郎碎片', 'fragment_type': '寿司郎', 'description': '寿司郎碎片（在背包中9个合成一个实际物品才能使用）'})
            else:
                results.append({'type': 'fragment', 'name': '水牛奶一箱', 'fragment_type': '水牛奶一箱', 'description': '水牛奶一箱（在背包中4个合成一个实际物品才能使用）'})
                
        elif draw_type == 'ultimate':
            # 超级抽奖的奖品和概率信息（修改版）
            if num_draws > 5:
                num_draws = 5
            if rand < 1.5:  # 1.50%
                results.append({'type': 'physical_item', 'name': '寿司郎一顿', 'description': '寿司郎一顿（实际物品）'})
            elif rand < 4.0:  # 2.50%
                results.append({'type': 'physical_item', 'name': '鸡胸肉套餐', 'description': '鸡胸肉套餐（实际物品）'})
            elif rand < 5.0:  # 1.00%
                results.append({'type': 'physical_item', 'name': '100r衣服兑换券', 'description': '100r衣服兑换券（实际物品）'})
            elif rand < 55.0:  # 50.00%
                results.append({'type': 'balance', 'value': 520, 'name': '520个宝宝币', 'description': '获得520个宝宝币'})
            elif rand < 57.5:  # 2.50%
                results.append({'type': 'coupon', 'value': 1.0, 'name': '免单券', 'description': '免单券'})
            elif rand < 60.0:  # 2.50%
                results.append({'type': 'balance', 'value': 5200, 'name': '5200个宝宝币', 'description': '获得5200个宝宝币'})
            elif rand < 75.0:  # 15.00%
                results.append({'type': 'balance', 'value': 1314, 'name': '1314个宝宝币', 'description': '获得1314个宝宝币'})
            elif rand < 81.5:  # 6.50%
                results.append({'type': 'balance', 'value': 52, 'name': '52个宝宝币', 'description': '获得52个宝宝币'})
            elif rand < 82.5:  # 1.00%
                results.append({'type': 'make_up_card', 'value': 1, 'name': '补签卡', 'description': '获得1张补签卡'})
            elif rand < 85.5:  # 3.00%
                results.append({'type': 'physical_item', 'name': '水牛奶', 'description': '水牛奶（实际物品）'})
            elif rand < 90.5:  # 5.00%
                results.append({'type': 'physical_item', 'name': '宝宝按摩30分钟', 'description': '宝宝按摩30分钟（实际物品）'})
            else:  # 10.00%
                results.append({'type': 'physical_item', 'name': '肠粉一顿', 'description': '肠粉一顿（实际物品）'})
                
        elif draw_type == 'legendary':
            # 究极抽奖的奖品和概率信息（只能单抽）
            if rand < 5.0:  # 5.00%
                results.append({'type': 'physical_item', 'name': '寿司郎一餐', 'description': '寿司郎一餐（实际物品）'})
            elif rand < 24.0:  # 19.00%
                results.append({'type': 'balance', 'value': 5200, 'name': '5200宝宝币', 'description': '获得5200个宝宝币'})
            elif rand < 64.0:  # 40.00%
                results.append({'type': 'balance', 'value': 1314, 'name': '1314宝宝币', 'description': '获得1314个宝宝币'})
            elif rand < 66.5:  # 2.50%
                results.append({'type': 'balance', 'value': 13140, 'name': '13140宝宝币', 'description': '获得13140个宝宝币'})
            elif rand < 69.5:  # 3.00%
                results.append({'type': 'physical_item', 'name': '奶茶鼠玩偶', 'description': '奶茶鼠玩偶（实际物品）'})
            elif rand < 89.5:  # 20.00%
                results.append({'type': 'physical_item', 'name': '新巴克', 'description': '新巴克（实际物品）'})
            elif rand < 94.5:  # 5.00%
                results.append({'type': 'fragment', 'name': 'switch碎片', 'fragment_type': 'switch', 'description': 'switch碎片（在背包中12个合成一个实际物品才能使用）'})
            else:  # 5.50%
                results.append({'type': 'physical_item', 'name': '按摩45分钟', 'description': '按摩45分钟（实际物品）'})
    
    return results

def add_item_to_inventory(user_data, item):
    """添加物品到背包"""
    if not 'inventory' in user_data:
        user_data['inventory'] = []
    
    # 检查是否已存在相同物品
    existing_item = None
    for inv_item in user_data['inventory']:
        # 对于碎片，根据fragment_type匹配
        if item['type'] == 'fragment' and inv_item.get('type') == 'fragment':
            if inv_item.get('fragment_type') == item.get('fragment_type'):
                existing_item = inv_item
                break
        # 对于其他物品，根据名称和类型匹配
        elif inv_item['name'] == item['name'] and inv_item['type'] == item['type']:
            existing_item = inv_item
            break
    
    if existing_item:
        existing_item['quantity'] += item.get('quantity', 1)
    else:
        item['quantity'] = item.get('quantity', 1)
        item['obtained_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_data['inventory'].append(item)

@app.route('/lottery_page')
def lottery_page():
    """抽奖页面"""
    user_data = load_user_data()
    
    # 检查用户是否拥有switch碎片
    has_switch_fragments = False
    for item in user_data.get('inventory', []):
        if (item.get('type') == 'fragment' and 
            item.get('fragment_type') == 'switch'):
            has_switch_fragments = True
            break
    
    return render_template('lottery.html', 
                         balance=user_data['balance'], 
                         has_switch_fragments=has_switch_fragments)

@app.route('/lottery_draw', methods=['POST'])
def lottery_draw():
    """处理抽奖请求"""
    data = request.get_json()
    draw_type = data.get('type')  # normal, premium, ultimate
    is_ten_draw = data.get('ten_draw', False)
    
    user_data = load_user_data()
    
    # 计算费用
    costs = {'normal': 52, 'premium': 520, 'ultimate': 1314, 'legendary': 5200}
    single_cost = costs.get(draw_type, 0)
    
    if is_ten_draw:
        if draw_type == 'premium':
            total_cost = single_cost * 7  # 高级七连抽
        elif draw_type == 'ultimate':
            total_cost = single_cost * 5  # 超级五连抽
        elif draw_type == 'legendary':
            total_cost = single_cost * 3  # 究极三连抽
        else:
            total_cost = single_cost * 10  # 普通十连抽
    else:
        total_cost = single_cost
    
    # 检查余额
    if user_data['balance'] < total_cost:
        return jsonify({'success': False, 'message': '宝宝币不足'})
    
    # 扣除费用
    user_data['balance'] -= total_cost
    
    # 添加消费记录
    transaction = {
        'id': str(uuid.uuid4())[:8],
        'amount': -total_cost,
        'description': f'{"七连" if is_ten_draw and draw_type == "premium" else "五连" if is_ten_draw and draw_type == "ultimate" else "三连" if is_ten_draw and draw_type == "legendary" else "十连" if is_ten_draw else "单次"}抽奖-{draw_type}',
        'type': 'expense',
        'timestamp': int(datetime.now().timestamp()),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    user_data['transactions'].insert(0, transaction)
    
    # 执行抽奖
    num_draws = 10 if is_ten_draw else 1
    if draw_type == 'premium':
        num_draws = 7 if is_ten_draw else 1
    elif draw_type == 'ultimate':
        num_draws = 5 if is_ten_draw else 1
    elif draw_type == 'legendary':
        num_draws = 3 if is_ten_draw else 1  # 究极可以三连抽
    results = perform_draw(draw_type, num_draws)
    
    # 处理奖励
    for result in results:
        if result['type'] == 'balance' or result['type'] == 'balance_deduction':
            user_data['balance'] += result['value']
            # 添加奖励记录
            if result['value'] != 0:
                reward_transaction = {
                    'id': str(uuid.uuid4())[:8],
                    'amount': result['value'],
                    'description': f'抽奖奖励-{result["name"]}',
                    'type': 'income' if result['value'] > 0 else 'expense',
                    'timestamp': int(datetime.now().timestamp()),
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                user_data['transactions'].insert(0, reward_transaction)
        
        elif result['type'] == 'make_up_card':
            if 'make_up_cards' not in user_data:
                user_data['make_up_cards'] = 0
            user_data['make_up_cards'] += result['value']
            add_item_to_inventory(user_data, {
                'type': 'consumable',
                'name': result['name'],
                'description': result['description'],
                'category': 'check_in_item',
                'value': result['value']
            })
        
        elif result['type'] == 'coupon':
            expires = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            coupon = {
                'id': str(uuid.uuid4())[:8],
                'type': 'discount' if result['value'] < 1.0 else 'free',
                'value': result['value'],
                'description': result['name'],
                'expires': expires,
                'used': False,
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'lottery'
            }
            user_data['coupons'].append(coupon)
            add_item_to_inventory(user_data, {
                'type': 'coupon',
                'name': result['name'],
                'description': result['description'],
                'category': 'discount_item',
                'coupon_id': coupon['id']
            })
        
        elif result['type'] == 'fragment':
            # 处理碎片物品
            add_item_to_inventory(user_data, {
                'type': 'fragment',
                'name': result['name'],
                'description': result['description'],
                'category': 'fragment_item',
                'fragment_type': result['fragment_type'],
                'obtained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        elif result['type'] == 'physical_item':
            add_item_to_inventory(user_data, {
                'type': 'physical',
                'name': result['name'],
                'description': result['description'],
                'category': 'real_item',
                'item_code': result.get('value', result['name']),
                'obtained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'results': results,
        'new_balance': user_data['balance']
    })

@app.route('/inventory_page')
def inventory_page():
    """背包页面"""
    user_data = load_user_data()
    return render_template('inventory.html', 
                         inventory=user_data.get('inventory', []),
                         balance=user_data['balance'])

@app.route('/delete_inventory_item', methods=['POST'])
def delete_inventory_item():
    """删除背包物品"""
    try:
        data = request.get_json()
        item_index = data.get('item_index')
        
        if item_index is None:
            return jsonify({'success': False, 'message': '缺少物品索引'})
        
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # 验证索引有效性
        if not isinstance(item_index, int) or item_index < 0 or item_index >= len(inventory):
            return jsonify({'success': False, 'message': '无效的物品索引'})
        
        # 获取要删除的物品信息
        item_to_delete = inventory[item_index]
        item_name = item_to_delete.get('name', '未知物品')
        
        # 删除物品
        del inventory[item_index]
        
        # 保存数据
        save_user_data(user_data)
        
        return jsonify({
            'success': True, 
            'message': f'已删除 "{item_name}"'
        })
        
    except Exception as e:
        print(f"删除物品出错: {e}")
        return jsonify({'success': False, 'message': '删除失败，请重试'})

@app.route('/compose_fragments', methods=['POST'])
def compose_fragments():
    """合成碎片"""
    data = request.get_json()
    fragment_type = data.get('fragment_type')
    
    if fragment_type not in FRAGMENT_RECIPES:
        return jsonify({'success': False, 'message': '未知的碎片类型'})
    
    user_data = load_user_data()
    inventory = user_data.get('inventory', [])
    
    # 统计该类型碎片的数量
    fragment_count = 0
    fragment_items = []
    
    for item in inventory:
        if (item.get('type') == 'fragment' and 
            item.get('fragment_type') == fragment_type):
            fragment_count += item.get('quantity', 1)
            fragment_items.append(item)
    
    recipe = FRAGMENT_RECIPES[fragment_type]
    fragments_needed = recipe['fragments_needed']
    
    if fragment_count < fragments_needed:
        return jsonify({
            'success': False, 
            'message': f'碎片不足！需要{fragments_needed}个，当前只有{fragment_count}个'
        })
    
    # 消耗碎片
    remaining_to_consume = fragments_needed
    items_to_remove = []
    
    for item in fragment_items:
        if remaining_to_consume <= 0:
            break
        
        item_quantity = item.get('quantity', 1)
        
        if item_quantity <= remaining_to_consume:
            # 完全消耗这个item
            remaining_to_consume -= item_quantity
            items_to_remove.append(item)
        else:
            # 部分消耗这个item
            item['quantity'] -= remaining_to_consume
            remaining_to_consume = 0
    
    # 移除完全消耗的物品
    for item in items_to_remove:
        if item in inventory:
            inventory.remove(item)
    
    # 添加合成的实际物品
    result_item = recipe['result_item'].copy()
    result_item['obtained_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result_item['source'] = f'碎片合成({fragment_type})'
    
    add_item_to_inventory(user_data, result_item)
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'message': f'成功合成{result_item["name"]}！',
        'result_item': result_item
    })

@app.route('/get_composable_fragments')
def get_composable_fragments():
    """获取可合成的碎片信息"""
    user_data = load_user_data()
    inventory = user_data.get('inventory', [])
    
    # 统计各种碎片的数量
    fragment_counts = {}
    
    for item in inventory:
        if item.get('type') == 'fragment':
            fragment_type = item.get('fragment_type')
            if fragment_type:
                if fragment_type not in fragment_counts:
                    fragment_counts[fragment_type] = 0
                fragment_counts[fragment_type] += item.get('quantity', 1)
    
    # 生成可合成信息
    composable_info = []
    
    for fragment_type, recipe in FRAGMENT_RECIPES.items():
        current_count = fragment_counts.get(fragment_type, 0)
        needed_count = recipe['fragments_needed']
        can_compose = current_count >= needed_count
        
        # 对于switch碎片，如果用户完全没有，则不显示在合成列表中（保持神秘感）
        if fragment_type == 'switch' and current_count == 0:
            continue
        
        composable_info.append({
            'fragment_type': fragment_type,
            'current_count': current_count,
            'needed_count': needed_count,
            'can_compose': can_compose,
            'result_item': recipe['result_item'],
            'how_many_can_compose': current_count // needed_count if current_count >= needed_count else 0
        })
    
    return jsonify({
        'success': True,
        'composable_fragments': composable_info
    })

@app.route('/use_item', methods=['POST'])
def use_item():
    """使用背包物品"""
    data = request.get_json()
    item_index = data.get('item_index')
    
    user_data = load_user_data()
    inventory = user_data.get('inventory', [])
    
    if item_index < 0 or item_index >= len(inventory):
        return jsonify({'success': False, 'message': '物品不存在'})
    
    item = inventory[item_index]
    
    if item['type'] == 'physical':
        # 实际物品 - 创建订单
        # 减少物品数量
        item['quantity'] -= 1
        if item['quantity'] <= 0:
            inventory.remove(item)
        
        # 创建订单
        order = {
            'id': str(uuid.uuid4())[:8],
            'customer_name': '宝包用户',
            'items': [
                {
                    'name': item['name'],
                    'price': 0,  # 实物奖励，价格为0
                    'quantity': 1,
                    'image': 'images/default.jpg',
                    'description': item['description']
                }
            ],
            'total_price': 0,
            'total_cost': 0,
            'status': 'pending',
            'timestamp': int(datetime.now().timestamp()),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'inventory',
            'payment_method': 'free'
        }
        
        # 保存订单
        save_order(order)
        
        # 保存用户数据
        save_user_data(user_data)
        
        return jsonify({
            'success': True,
            'message': f'{item["name"]}订单已创建！厨师端将收到通知。',
            'order_id': order['id']
        })
    
    elif item['type'] == 'fragment':
        # 碎片物品不能直接使用，需要合成
        return jsonify({
            'success': False, 
            'message': '碎片无法直接使用，请先合成为实际物品',
            'action': 'compose',
            'fragment_type': item.get('fragment_type')
        })
    
    elif item['type'] == 'consumable' and item['category'] == 'check_in_item':
        # 补签卡在背包中只能查看，实际使用在补签界面
        return jsonify({
            'success': False, 
            'message': '请在签到页面使用补签卡',
            'action': 'redirect',
            'url': '/check_in_page'
        })
    
    elif item['type'] == 'coupon':
        # 优惠券在购物时自动使用
        return jsonify({
            'success': False, 
            'message': '优惠券将在购物时自动应用',
            'action': 'redirect',
            'url': '/customer'
        })
    
    return jsonify({'success': False, 'message': '该物品不能直接使用'})

# 寻宝日记游戏相关函数
def generate_treasure_map_rewards():
    """生成50格地图的随机奖励，包含特殊格子"""
    rewards = []
    special_types = []  # 标记特殊格子类型
    
    # 生成基础格子奖励（-52到+119宝宝币）
    for i in range(50):
        reward = random.randint(-52, 119)
        rewards.append(reward)
        special_types.append('normal')  # 普通格子
    
    # 随机选择两个不同的位置放置特殊格子
    special_positions = random.sample(range(50), 2)
    
    # 第一个位置放宝藏格子
    treasure_pos = special_positions[0]
    rewards[treasure_pos] = 1314
    special_types[treasure_pos] = 'treasure'
    
    # 第二个位置放裂开格子
    crack_pos = special_positions[1]
    rewards[crack_pos] = -520
    special_types[crack_pos] = 'crack'
    
    return rewards, special_types

def calculate_completion_reward():
    """计算完圈奖励"""
    rand = random.random() * 100
    
    if rand < 60:  # 60%
        return {
            'type': 'coupon',
            'value': 0.9,
            'name': '9折优惠券',
            'description': '获得9折优惠券'
        }
    elif rand < 80:  # 20%
        return {
            'type': 'coupon',
            'value': 0.8,
            'name': '8折优惠券',
            'description': '获得8折优惠券'
        }
    elif rand < 90:  # 10%
        return {
            'type': 'physical_item',
            'value': 'milk_tea_card',
            'name': '奶茶卡',
            'description': '一杯奶茶卡（实物）'
        }
    elif rand < 95:  # 5%
        return {
            'type': 'balance',
            'value': 520,
            'name': '宝宝币大奖',
            'description': '获得520个宝宝币'
        }
    elif rand < 96:  # 1%
        return {
            'type': 'balance',
            'value': 1314,
            'name': '宝宝币超级大奖',
            'description': '获得1314个宝宝币'
        }
    elif rand < 97:  # 1%
        return {
            'type': 'physical_item',
            'value': 'starbucks_card',
            'name': '星巴克卡',
            'description': '星巴克实体卡片'
        }
    else:  # 3%
        return {
            'type': 'coupon',
            'value': 1.0,
            'name': '免单券',
            'description': '获得免单券'
        }

@app.route('/treasure_hunt')
def treasure_hunt():
    """寻宝日记游戏页面"""
    user_data = load_user_data()
    
    # 初始化寻宝日记游戏数据
    if 'treasure_hunt' not in user_data:
        map_rewards, special_types = generate_treasure_map_rewards()
        user_data['treasure_hunt'] = {
            'current_position': 0,  # 当前位置（0-49）
            'map_rewards': map_rewards,  # 地图奖励
            'special_types': special_types,  # 特殊格子类型
            'completed_rounds': 0,  # 完成的圈数
            'total_earned': 0,  # 总收入
            'last_reset_date': datetime.now().strftime('%Y-%m-%d'),
            'completion_rewards_claimed': []  # 已领取的完圈奖励
        }
        save_user_data(user_data)
    
    # 检查是否需要重置地图奖励（每天重置一次）
    today = datetime.now().strftime('%Y-%m-%d')
    if user_data['treasure_hunt']['last_reset_date'] != today:
        map_rewards, special_types = generate_treasure_map_rewards()
        user_data['treasure_hunt']['map_rewards'] = map_rewards
        user_data['treasure_hunt']['special_types'] = special_types
        user_data['treasure_hunt']['last_reset_date'] = today
        save_user_data(user_data)
    
    return render_template('treasure_hunt.html',
                         balance=user_data['balance'],
                         treasure_data=user_data['treasure_hunt'],
                         map_rewards=user_data['treasure_hunt']['map_rewards'],
                         special_types=user_data['treasure_hunt'].get('special_types', ['normal'] * 50))

@app.route('/buy_treasure_dice', methods=['POST'])
def buy_treasure_dice():
    """购买寻宝日记游戏骰子"""
    user_data = load_user_data()
    
    # 检查余额
    if user_data['balance'] < 52:
        return jsonify({'success': False, 'message': '宝宝币不足！需要52个宝宝币。'})
    
    # 扣除宝宝币
    success, message = add_transaction(52, '购买寻宝日记骰子', 'expense')
    if not success:
        return jsonify({'success': False, 'message': message})
    
    # 投掷骰子
    dice_result = random.randint(1, 6)
    
    # 更新用户数据
    user_data = load_user_data()
    if 'treasure_hunt' not in user_data:
        map_rewards, special_types = generate_treasure_map_rewards()
        user_data['treasure_hunt'] = {
            'current_position': 0,
            'map_rewards': map_rewards,
            'special_types': special_types,
            'completed_rounds': 0,
            'total_earned': 0,
            'last_reset_date': datetime.now().strftime('%Y-%m-%d'),
            'completion_rewards_claimed': []
        }
    
    # 计算新位置
    old_position = user_data['treasure_hunt']['current_position']
    new_position = (old_position + dice_result) % 50
    
    # 检查是否完成一圈
    completed_round = (old_position + dice_result) >= 50 and old_position < 50
    if completed_round:
        user_data['treasure_hunt']['completed_rounds'] += 1
    
    user_data['treasure_hunt']['current_position'] = new_position
    
    # 获取格子奖励和类型
    grid_reward = user_data['treasure_hunt']['map_rewards'][new_position]
    grid_type = user_data['treasure_hunt'].get('special_types', ['normal'] * 50)[new_position]
    
    # 应用奖励
    if grid_reward != 0:
        user_data['balance'] += grid_reward
        user_data['treasure_hunt']['total_earned'] += grid_reward
        
        # 根据格子类型设置描述
        if grid_type == 'treasure':
            transaction_desc = f'寻宝日记宝藏格子奖励(第{new_position + 1}格)'
        elif grid_type == 'crack':
            transaction_desc = f'寻宝日记裂开格子惩罚(第{new_position + 1}格)'
        else:
            transaction_desc = f'寻宝日记格子奖励(第{new_position + 1}格)'
            
        # 添加交易记录
        transaction = {
            'id': str(uuid.uuid4())[:8],
            'amount': grid_reward,
            'description': transaction_desc,
            'type': 'income' if grid_reward > 0 else 'expense',
            'timestamp': int(datetime.now().timestamp()),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        user_data['transactions'].insert(0, transaction)
    
    # 如果完成一圈，重新生成地图奖励
    if completed_round:
        map_rewards, special_types = generate_treasure_map_rewards()
        user_data['treasure_hunt']['map_rewards'] = map_rewards
        user_data['treasure_hunt']['special_types'] = special_types
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'dice_result': dice_result,
        'old_position': old_position,
        'new_position': new_position,
        'grid_reward': grid_reward,
        'grid_type': grid_type,
        'completed_round': completed_round,
        'new_balance': user_data['balance'],
        'map_rewards': user_data['treasure_hunt']['map_rewards'],
        'special_types': user_data['treasure_hunt'].get('special_types', ['normal'] * 50)
    })

@app.route('/claim_completion_reward', methods=['POST'])
def claim_completion_reward():
    """领取完圈奖励"""
    user_data = load_user_data()
    
    if 'treasure_hunt' not in user_data:
        return jsonify({'success': False, 'message': '游戏数据不存在'})
    
    # 检查是否有可领取的完圈奖励
    completed_rounds = user_data['treasure_hunt']['completed_rounds']
    claimed_rewards = len(user_data['treasure_hunt']['completion_rewards_claimed'])
    
    if completed_rounds <= claimed_rewards:
        return jsonify({'success': False, 'message': '没有可领取的完圈奖励'})
    
    # 生成完圈奖励
    reward = calculate_completion_reward()
    
    # 应用奖励
    if reward['type'] == 'balance':
        user_data['balance'] += reward['value']
        # 添加交易记录
        transaction = {
            'id': str(uuid.uuid4())[:8],
            'amount': reward['value'],
            'description': f'寻宝日记完圈奖励-{reward["name"]}',
            'type': 'income',
            'timestamp': int(datetime.now().timestamp()),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        user_data['transactions'].insert(0, transaction)
        
    elif reward['type'] == 'coupon':
        expires = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        coupon = {
            'id': str(uuid.uuid4())[:8],
            'type': 'discount' if reward['value'] < 1.0 else 'free',
            'value': reward['value'],
            'description': reward['name'],
            'expires': expires,
            'used': False,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'treasure_hunt'
        }
        user_data['coupons'].append(coupon)
        add_item_to_inventory(user_data, {
            'type': 'coupon',
            'name': reward['name'],
            'description': reward['description'],
            'category': 'discount_item',
            'coupon_id': coupon['id']
        })
        
    elif reward['type'] == 'physical_item':
        add_item_to_inventory(user_data, {
            'type': 'physical',
            'name': reward['name'],
            'description': reward['description'],
            'category': 'real_item',
            'item_code': reward['value']
        })
    
    # 记录已领取的奖励
    user_data['treasure_hunt']['completion_rewards_claimed'].append({
        'reward': reward,
        'claimed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'reward': reward,
        'new_balance': user_data['balance'],
        'remaining_rewards': completed_rounds - len(user_data['treasure_hunt']['completion_rewards_claimed'])
    })

@app.route('/chef/seeds', methods=['GET'])
def get_seeds():
    """获取种子数据"""
    try:
        seeds_data = load_seeds_data()
        return jsonify({
            'success': True,
            'seeds': seeds_data['seeds']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/chef/seeds/add', methods=['POST'])
def add_seed():
    """添加新种子"""
    try:
        data = request.get_json()
        seeds_data = load_seeds_data()
        
        # 检查种子ID是否已存在
        if data['id'] in seeds_data['seeds']:
            return jsonify({
                'success': False,
                'message': '种子ID已存在，请使用不同的ID'
            })
        
        # 添加新种子
        seeds_data['seeds'][data['id']] = data
        save_seeds_data(seeds_data)
        
        return jsonify({
            'success': True,
            'message': '种子添加成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/chef/seeds/toggle', methods=['POST'])
def toggle_seed_availability():
    """切换种子上架/下架状态"""
    try:
        data = request.get_json()
        seed_id = data['seed_id']
        available = data['available']
        
        seeds_data = load_seeds_data()
        
        if seed_id not in seeds_data['seeds']:
            return jsonify({
                'success': False,
                'message': '种子不存在'
            })
        
        seeds_data['seeds'][seed_id]['available'] = available
        save_seeds_data(seeds_data)
        
        action = '上架' if available else '下架'
        return jsonify({
            'success': True,
            'message': f'种子{action}成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/chef/seeds/delete', methods=['POST'])
def delete_seed():
    """删除种子"""
    try:
        data = request.get_json()
        seed_id = data['seed_id']
        
        seeds_data = load_seeds_data()
        
        if seed_id not in seeds_data['seeds']:
            return jsonify({
                'success': False,
                'message': '种子不存在'
            })
        
        del seeds_data['seeds'][seed_id]
        save_seeds_data(seeds_data)
        
        return jsonify({
            'success': True,
            'message': '种子删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, host='0.0.0.0', port=port)