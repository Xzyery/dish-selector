import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    # 使用简化的Vercel适配版本
    from web.app_vercel import app
except Exception as e:
    # 如果导入失败，创建一个简单的错误处理应用
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_handler():
        return jsonify({
            'error': f'Application failed to start: {str(e)}',
            'path': sys.path,
            'cwd': os.getcwd(),
            'files': os.listdir('.')
        }), 500
    
    @app.route('/debug')
    def debug_info():
        return jsonify({
            'python_version': sys.version,
            'path': sys.path,
            'cwd': os.getcwd(),
            'env_vars': dict(os.environ),
            'directory_contents': {
                'root': os.listdir('.'),
                'web': os.listdir('./web') if os.path.exists('./web') else 'not found'
            }
        })