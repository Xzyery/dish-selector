#!/bin/bash

# Render部署启动脚本

# 设置工作目录
cd web

# 使用Gunicorn启动Flask应用
gunicorn --bind 0.0.0.0:$PORT app:app