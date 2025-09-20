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

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dish_selector_secret_key_2024')

# Vercel适配：使用相对路径和临时目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('/tmp', 'static') if os.environ.get('VERCEL') else os.path.join(BASE_DIR, 'static')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 数据文件路径 - Vercel适配
if os.environ.get('VERCEL'):
    # Vercel环境：使用/tmp临时目录
    DISHES_FILE = '/tmp/dishes.json'
    ORDERS_DIR = '/tmp/orders'
    USER_DATA_FILE = '/tmp/user_data.json'
    QUESTIONNAIRE_FILE = '/tmp/questionnaire_responses.json'
    SEEDS_FILE = '/tmp/seeds_data.json'
else:
    # 本地环境
    DISHES_FILE = os.path.join(BASE_DIR, 'dishes.json')
    ORDERS_DIR = os.path.join(BASE_DIR, 'orders')
    USER_DATA_FILE = os.path.join(BASE_DIR, 'user_data.json')
    QUESTIONNAIRE_FILE = os.path.join(BASE_DIR, 'questionnaire_responses.json')
    SEEDS_FILE = os.path.join(BASE_DIR, 'seeds_data.json')

# 确保必要的目录存在
for directory in [UPLOAD_FOLDER, ORDERS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# 初始化默认数据文件
def init_default_files():
    """初始化默认数据文件"""
    # 初始化菜品数据
    if not os.path.exists(DISHES_FILE):
        default_dishes = [
            {
                "name": "麻婆豆腐",
                "image_path": "images/fish.jpeg",
                "price": 45
            },
            {
                "name": "宫保鸡丁", 
                "image_path": "images/fish.jpeg",
                "price": 52
            }
        ]
        with open(DISHES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_dishes, f, ensure_ascii=False, indent=2)
    
    # 初始化种子数据
    if not os.path.exists(SEEDS_FILE):
        default_seeds = {
            "seeds": {
                "tomato_seed": {
                    "id": "tomato_seed", 
                    "name": "番茄种子",
                    "description": "新鲜的番茄种子",
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
        with open(SEEDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_seeds, f, ensure_ascii=False, indent=2)

# 在Vercel环境中初始化文件
if os.environ.get('VERCEL'):
    init_default_files()

# 导入原始app.py的所有函数和路由
# 这里我们需要复制原始app.py中的所有内容
# 为了简化，我们创建一个导入机制

try:
    # 动态导入原始app.py的内容
    import sys
    sys.path.insert(0, BASE_DIR)
    
    # 读取原始app.py并执行其中的函数定义
    with open(os.path.join(BASE_DIR, 'app.py'), 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # 移除原始文件中的app创建和运行部分
    lines = app_content.split('\n')
    filtered_lines = []
    skip_lines = False
    
    for line in lines:
        if 'app = Flask(__name__)' in line:
            skip_lines = True
            continue
        elif "if __name__ == '__main__':" in line:
            break
        elif not skip_lines or (skip_lines and line.startswith('def ') or line.startswith('@')):
            skip_lines = False
        
        if not skip_lines:
            filtered_lines.append(line)
    
    # 执行过滤后的代码
    exec('\n'.join(filtered_lines))
    
except Exception as e:
    print(f"Error importing app.py: {e}")
    # 如果导入失败，提供基本的路由
    @app.route('/')
    def index():
        return "WXZY点餐系统 - Vercel部署版本"

# Vercel要求的应用程序入口点
if __name__ == '__main__':
    app.run(debug=False)
else:
    # Vercel serverless环境
    app.wsgi_app = app.wsgi_app