#!/bin/bash

# 启动脚本 - 用于Render部署

# 安装依赖
pip install -r requirements.txt

# 创建必要的目录
mkdir -p web/static/images
mkdir -p orders

# 启动Flask应用
cd web
python app.py