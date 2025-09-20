# 部署说明

## 本地运行

1. 克隆项目
```bash
git clone https://github.com/你的用户名/dish-selector.git
cd dish-selector
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动应用
```bash
cd web
python app.py
```

4. 访问应用
- 主页: http://127.0.0.1:5000
- 厨师端: http://127.0.0.1:5000/chef
- 客户端: http://127.0.0.1:5000/customer

## 云端部署

### Heroku部署
1. 创建Heroku应用
2. 连接GitHub仓库
3. 自动部署（使用Procfile和runtime.txt）

### Railway部署
1. 连接GitHub仓库
2. 选择Python环境
3. 自动检测并部署

### Render部署
1. 连接GitHub仓库
2. 选择Web Service
3. 构建命令: `pip install -r requirements.txt`
4. 启动命令: `cd web && python app.py`

## 环境变量（可选）
- `PORT`: 端口号（默认5000）
- `SECRET_KEY`: Flask密钥（生产环境建议设置）

## 文件说明
- `web/app.py`: 主应用文件
- `web/templates/`: HTML模板
- `web/static/`: 静态资源
- `web/seeds_data.json`: 农场种子数据
- `requirements.txt`: Python依赖
- `Procfile`: 部署配置