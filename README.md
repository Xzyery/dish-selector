# WXZY点餐系统# WXZY点餐系统



一个现代化的餐厅点餐Web系统，提供厨师管理端和顾客点餐端。一个现代化的餐厅点餐Web系统，提供厨师管理端和顾客点餐端。



## 系统特色## 🌟 功能特性



- **角色分离**：厨师管理端和顾客点餐端### 🖥️ 桌面版（Tkinter）

- **实时订单**：支持添加菜品、修改订单和生成订单链接- 📋 查看所有菜品列表

- **图片管理**：支持菜品图片上传和显示- ➕ 添加新菜品（名称 + 图片）

- **现代设计**：响应式Web界面，友好的用户体验- 🗑️ 删除现有菜品

- 🖼️ 菜品图片预览

## 项目结构- 🎲 随机推荐菜品

- 🛒 购物车管理和下单功能

```

dish-selector/### 🌐 Web版（Flask）

├── web/                   # Web应用#### 🔧 厨师管理端

│   ├── app.py            # Flask主程序- **菜品管理**: 添加、删除菜品，支持图片上传

│   ├── templates/        # HTML模板- **订单管理**: 实时查看和处理客户订单

│   └── static/          # 静态资源- **客户链接**: 生成专属客户点餐链接

├── images/              # 菜品图片存储- **实时更新**: 自动刷新订单状态

├── orders/              # 订单数据存储

├── dishes.json          # 菜品数据#### � 客户点餐端

└── requirements.txt     # 项目依赖- **菜品浏览**: 精美的菜品图片展示

```- **购物车**: 便捷的购物车管理

- **随机推荐**: 智能菜品推荐功能

## 功能介绍- **订单提交**: 简单快捷的下单流程



### 🍳 厨师端功能#### 🎨 界面设计

- 添加新菜品（名称、价格、图片）- **响应式设计**: 适配各种屏幕尺寸

- 编辑现有菜品信息- **现代UI**: 使用Bootstrap 5构建美观界面

- 删除菜品- **图标系统**: Font Awesome图标增强用户体验

- 查看所有订单- **颜色主题**: 淡蓝色渐变背景，专业餐厅风格

- 删除已完成订单

## 🚀 快速开始

### 🍽️ 顾客端功能  

- 浏览所有可用菜品### 环境要求

- 添加菜品到订单- Python 3.7+

- 查看订单详情和总价- pip包管理器

- 提交订单

### 安装步骤

## 快速开始

1. **克隆项目**

### 环境要求   ```bash

- Python 3.7+   git clone https://github.com/你的用户名/wxzy-restaurant-system.git

- pip   cd wxzy-restaurant-system

   ```

### 安装步骤

2. **安装依赖**

1. 克隆项目   ```bash

```bash   pip install -r requirements.txt

git clone https://github.com/你的用户名/dish-selector.git   ```

cd dish-selector

```### 运行桌面版

```bash

2. 安装依赖cd src

```bashpython main.py

pip install -r requirements.txt```

```

### 运行Web版

3. 启动Web服务器```bash

```bashcd web

cd webpython app.py

python app.py```

```然后在浏览器中访问:

- 主页: `http://127.0.0.1:5000`

4. 在浏览器中访问：- 厨师端: `http://127.0.0.1:5000/chef`

   - 主页：http://127.0.0.1:5000- 客户端: `http://127.0.0.1:5000/customer`

   - 厨师端：http://127.0.0.1:5000/chef  

   - 顾客端：http://127.0.0.1:5000/customer## 使用说明



## 使用说明1. 运行程序后会出现选择界面

2. 选择"厨师端"进行菜品管理

### 使用流程3. 选择"顾客端"进行点餐

4. 菜品数据保存在 `dishes.json` 文件中

1. **访问系统主页**，选择身份：5. 菜品图片存储在 `images/` 文件夹中

   - 点击"厨师入口"进入管理界面

   - 点击"顾客入口"开始点餐## 📁 项目结构



2. **厨师端操作**：```

   - 在厨师界面添加新菜品dish-selector/

   - 上传图片并设置菜品信息├── README.md                 # 项目说明文档

   - 查看和管理所有订单├── requirements.txt          # Python依赖包列表

   - 为顾客生成专属点餐链接├── check_data.py            # 数据检查脚本

├── dishes.json              # 菜品数据文件

3. **顾客端操作**：├── images/                  # 菜品图片目录

   - 浏览所有可用菜品│   ├── dish_*.jpg/png       # 菜品图片文件

   - 点击"加入订单"添加心仪菜品│   └── fish.jpeg           # 示例图片

   - 查看订单详情和总金额├── src/                     # 桌面版Tkinter应用源码

   - 提交最终订单│   ├── main.py             # 主程序入口

│   ├── chef_app.py         # 厨师应用模块

## 技术栈│   ├── customer_app.py     # 客户应用模块

│   ├── dishes/             # 菜品模块

- **Flask 2.3.3**：Web框架│   ├── mytypes/            # 类型定义模块

- **Jinja2**：模板引擎  │   └── utils/              # 工具模块

- **Bootstrap 5**：前端CSS框架└── web/                     # Flask Web应用

- **Font Awesome 6**：图标库    ├── app.py              # Flask主应用

- **Pillow 10.0.1**：图像处理    ├── orders/             # 订单存储目录

    ├── static/             # 静态文件

## 数据存储    │   └── css/

    │       └── style.css   # 自定义样式

- **菜品数据**：存储在 `dishes.json` 文件中    └── templates/          # 模板文件

- **订单数据**：存储在 `orders/` 目录中的JSON文件        ├── base.html       # 基础模板

- **图片文件**：存储在 `images/` 目录中        ├── index.html      # 首页模板

        ├── chef.html       # 厨师端模板

## 开发团队        └── customer.html   # 客户端模板

```

WXZY开发团队

## 🛠️ 技术栈

## 许可证

### 桌面版技术

MIT License- **界面**: Tkinter
- **图片处理**: Pillow (PIL)
- **数据存储**: JSON
- **语言**: Python 3

### Web版技术
#### 后端技术
- **Flask 2.3.3**: Python Web框架
- **Pillow 10.0.1**: 图像处理库
- **Python 3**: 编程语言

#### 前端技术
- **Bootstrap 5**: CSS框架
- **jQuery**: JavaScript库
- **Font Awesome 6**: 图标库
- **HTML5/CSS3**: 标记和样式

## 🎯 使用说明

### 桌面版操作流程
1. 运行程序后会出现选择界面
2. 选择"厨师端"进行菜品管理
3. 选择"顾客端"进行点餐
4. 菜品数据保存在 `dishes.json` 文件中
5. 菜品图片存储在 `images/` 文件夹中

### Web版操作流程
#### 厨师端操作流程
1. 访问厨师管理端页面 (`/chef`)
2. 使用"添加菜品"功能上传菜品图片和信息
3. 通过"生成客户链接"创建专属客户点餐链接
4. 实时查看客户订单并处理

#### 客户端操作流程
1. 通过厨师提供的链接或直接访问客户端 (`/customer`)
2. 浏览菜品并添加到购物车
3. 使用"随机推荐"发现新菜品
4. 填写个人信息并提交订单

## 🚀 部署说明

### 开发环境
1. 确保Python 3.7+已安装
2. 安装项目依赖: `pip install -r requirements.txt`
3. 桌面版运行: `python src/main.py`
4. Web版运行: `python web/app.py`
5. Web版访问: `http://127.0.0.1:5000`

### 生产环境（Web版）
建议使用Gunicorn或uWSGI作为WSGI服务器：
```bash
pip install gunicorn
cd web
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

1. Fork项目
2. 创建功能分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请联系：
- 项目作者: XZY
- GitHub: [你的GitHub用户名]

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！
