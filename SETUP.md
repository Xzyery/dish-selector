# WXZY点餐系统

一个现代化的餐厅点餐Web系统，提供厨师管理端和顾客点餐端，包含完整的游戏化功能。

## 🌟 主要功能

### 🍳 厨师管理端
- **菜品管理**: 添加、删除菜品，支持图片上传
- **订单管理**: 实时查看和处理客户订单  
- **用户管理**: 管理客户宝宝币余额和优惠券
- **数据查看**: 查看客户问卷回答和游戏记录

### 🍽️ 客户点餐端
- **菜品浏览**: 精美的菜品图片展示
- **购物车**: 便捷的购物车管理
- **优惠券**: 支持多种优惠券使用
- **随机推荐**: 智能菜品推荐功能

### 🎮 游戏化功能
- **每日任务**: 问卷调查、签到系统
- **游戏娱乐**: 猜数字游戏、抽奖系统、寻宝游戏
- **农场系统**: 种植作物、收获奖励
- **背包系统**: 物品管理、碎片合成

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip包管理器

### 本地运行

1. **克隆项目**
   ```bash
   git clone https://github.com/你的用户名/dish-selector.git
   cd dish-selector
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务器**
   ```bash
   cd web
   python app.py
   ```

4. **访问系统**
   - 主页: http://127.0.0.1:5000
   - 厨师端: http://127.0.0.1:5000/chef
   - 客户端: http://127.0.0.1:5000/customer

## 🌐 在线部署

### Heroku部署
```bash
# 安装Heroku CLI后
heroku create your-app-name
git push heroku main
```

### Railway部署
1. 连接GitHub仓库到Railway
2. 自动部署，无需额外配置

### Render部署
1. 连接GitHub仓库到Render
2. 设置构建命令: `pip install -r requirements.txt`
3. 设置启动命令: `cd web && python app.py`

## 📁 项目结构

```
dish-selector/
├── web/                    # Web应用主目录
│   ├── app.py             # Flask主程序
│   ├── templates/         # HTML模板
│   ├── static/           # 静态资源(CSS/图片)
│   ├── dishes.json       # 菜品数据
│   └── seeds_data.json   # 种子数据
├── requirements.txt       # Python依赖
├── Procfile              # 部署配置
├── runtime.txt           # Python版本
└── README.md             # 项目说明
```

## 🛠️ 技术栈

- **后端**: Flask 2.3.3
- **前端**: Bootstrap 5 + jQuery
- **图像处理**: Pillow 10.0.1
- **数据存储**: JSON文件
- **部署**: 支持Heroku/Railway/Render

## 🎯 系统特色

- **响应式设计**: 适配各种屏幕尺寸
- **实时交互**: Ajax异步通信
- **文件上传**: 支持图片上传和处理
- **数据持久化**: JSON文件存储用户数据
- **游戏化体验**: 完整的积分和奖励系统

## 📝 默认数据

系统启动后会自动创建必要的数据文件：
- `user_data.json` - 用户数据（余额、交易记录等）
- `questionnaire_responses.json` - 问卷回答记录
- `orders/` - 订单存储目录

## 🔧 开发说明

### 添加新功能
1. 在`app.py`中添加路由处理
2. 在`templates/`中添加或修改HTML模板
3. 在`static/`中添加CSS/JS资源

### 数据库迁移
当前使用JSON文件存储，如需使用数据库：
1. 安装数据库驱动 (如SQLite、PostgreSQL)
2. 修改`app.py`中的数据存储逻辑
3. 创建数据表结构

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请创建Issue或联系项目维护者。

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！