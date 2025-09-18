# WXZY点餐系统

一个现代化的双端菜品管理系统，包含基于Tkinter的桌面版本和基于Flask的Web版本。提供厨师端（管理菜品）和顾客端（点餐系统）的完整解决方案。

## 🌟 功能特性

### 🖥️ 桌面版（Tkinter）
- 📋 查看所有菜品列表
- ➕ 添加新菜品（名称 + 图片）
- 🗑️ 删除现有菜品
- 🖼️ 菜品图片预览
- 🎲 随机推荐菜品
- 🛒 购物车管理和下单功能

### 🌐 Web版（Flask）
#### 🔧 厨师管理端
- **菜品管理**: 添加、删除菜品，支持图片上传
- **订单管理**: 实时查看和处理客户订单
- **客户链接**: 生成专属客户点餐链接
- **实时更新**: 自动刷新订单状态

#### � 客户点餐端
- **菜品浏览**: 精美的菜品图片展示
- **购物车**: 便捷的购物车管理
- **随机推荐**: 智能菜品推荐功能
- **订单提交**: 简单快捷的下单流程

#### 🎨 界面设计
- **响应式设计**: 适配各种屏幕尺寸
- **现代UI**: 使用Bootstrap 5构建美观界面
- **图标系统**: Font Awesome图标增强用户体验
- **颜色主题**: 淡蓝色渐变背景，专业餐厅风格

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/你的用户名/wxzy-restaurant-system.git
   cd wxzy-restaurant-system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 运行桌面版
```bash
cd src
python main.py
```

### 运行Web版
```bash
cd web
python app.py
```
然后在浏览器中访问:
- 主页: `http://127.0.0.1:5000`
- 厨师端: `http://127.0.0.1:5000/chef`
- 客户端: `http://127.0.0.1:5000/customer`

## 使用说明

1. 运行程序后会出现选择界面
2. 选择"厨师端"进行菜品管理
3. 选择"顾客端"进行点餐
4. 菜品数据保存在 `dishes.json` 文件中
5. 菜品图片存储在 `images/` 文件夹中

## 📁 项目结构

```
dish-selector/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖包列表
├── check_data.py            # 数据检查脚本
├── dishes.json              # 菜品数据文件
├── images/                  # 菜品图片目录
│   ├── dish_*.jpg/png       # 菜品图片文件
│   └── fish.jpeg           # 示例图片
├── src/                     # 桌面版Tkinter应用源码
│   ├── main.py             # 主程序入口
│   ├── chef_app.py         # 厨师应用模块
│   ├── customer_app.py     # 客户应用模块
│   ├── dishes/             # 菜品模块
│   ├── mytypes/            # 类型定义模块
│   └── utils/              # 工具模块
└── web/                     # Flask Web应用
    ├── app.py              # Flask主应用
    ├── orders/             # 订单存储目录
    ├── static/             # 静态文件
    │   └── css/
    │       └── style.css   # 自定义样式
    └── templates/          # 模板文件
        ├── base.html       # 基础模板
        ├── index.html      # 首页模板
        ├── chef.html       # 厨师端模板
        └── customer.html   # 客户端模板
```

## 🛠️ 技术栈

### 桌面版技术
- **界面**: Tkinter
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
