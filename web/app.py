from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import shutil

app = Flask(__name__)
app.secret_key = 'dish_selector_secret_key_2024'

# 配置文件上传
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 数据文件路径
DISHES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dishes.json')
ORDERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'orders')

# 确保必要的目录存在
for directory in [UPLOAD_FOLDER, ORDERS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_dishes():
    """加载菜品数据"""
    if not os.path.exists(DISHES_FILE):
        with open(DISHES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    try:
        with open(DISHES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
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
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def index():
    """主页 - 选择进入厨师端或客户端"""
    return render_template('index.html')

@app.route('/chef')
def chef():
    """厨师端主页"""
    dishes = load_dishes()
    orders = load_orders()
    return render_template('chef.html', dishes=dishes, orders=orders)

@app.route('/customer')
def customer():
    """客户端主页"""
    dishes = load_dishes()
    return render_template('customer.html', dishes=dishes)

@app.route('/customer/<customer_id>')
def customer_with_id(customer_id):
    """带有客户ID的客户端（用于分享链接）"""
    dishes = load_dishes()
    return render_template('customer.html', dishes=dishes, customer_id=customer_id)

@app.route('/add_dish', methods=['POST'])
def add_dish():
    """添加新菜品"""
    dish_name = request.form.get('dish_name', '').strip()
    
    if not dish_name:
        flash('请输入菜品名称', 'error')
        return redirect(url_for('chef'))
    
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
                'image_path': f'images/{filename}'
            }
            dishes.append(new_dish)
            save_dishes(dishes)
            
            flash(f'菜品 "{dish_name}" 添加成功！', 'success')
            
        except Exception as e:
            flash(f'添加菜品失败: {str(e)}', 'error')
    else:
        flash('不支持的图片格式，请选择 PNG、JPG、JPEG、GIF 或 BMP 格式', 'error')
    
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
    customer_name = data.get('customer_name', '匿名客户').strip()
    selected_dishes = data.get('selected_dishes', [])
    customer_id = data.get('customer_id', 'unknown')
    
    if not selected_dishes:
        return jsonify({'success': False, 'message': '请选择菜品'})
    
    if not customer_name:
        customer_name = '匿名客户'
    
    # 创建订单
    order_id = str(uuid.uuid4())[:8]
    order = {
        'id': order_id,
        'customer_name': customer_name,
        'customer_id': customer_id,
        'dishes': selected_dishes,
        'timestamp': int(datetime.now().timestamp()),
        'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending'
    }
    
    try:
        save_order(order)
        return jsonify({'success': True, 'message': '订单提交成功！', 'order_id': order_id})
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)