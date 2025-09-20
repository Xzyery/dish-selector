# Vercel部署指南

## 🚀 快速部署到Vercel

### 方法一：GitHub自动部署（推荐）

1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "准备Vercel部署"
   git push origin main
   ```

2. **访问Vercel控制台**
   - 访问 [vercel.com](https://vercel.com)
   - 使用GitHub账号登录

3. **导入项目**
   - 点击 "New Project"
   - 选择你的 `dish-selector` 仓库
   - 点击 "Import"

4. **配置项目**
   - Project Name: `dish-selector`
   - Framework Preset: `Other`
   - Root Directory: `./` (保持默认)
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: `pip install -r requirements.txt`

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约2-3分钟）

### 方法二：Vercel CLI部署

1. **安装Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **登录Vercel**
   ```bash
   vercel login
   ```

3. **部署项目**
   ```bash
   vercel
   ```

4. **按提示配置**
   - Link to existing project? `N`
   - Project name: `dish-selector`
   - Directory: `./` (回车使用当前目录)

## 🔧 部署后配置

### 环境变量（可选）
在Vercel项目设置中添加：
- `SECRET_KEY`: 你的Flask密钥
- `PYTHON_VERSION`: `3.11.9`

### 自定义域名（可选）
1. 进入项目设置
2. 点击 "Domains"
3. 添加你的自定义域名

## 📊 部署状态检查

部署成功后，你会得到一个类似这样的URL：
- `https://dish-selector-[随机字符].vercel.app`

访问以下页面测试功能：
- 主页: `/`
- 厨师端: `/chef`
- 客户端: `/customer`

## ⚠️ Vercel限制说明

### 无服务器限制
- 每个函数最大执行时间：30秒
- 文件存储是临时的（重启后丢失）
- 适合演示和测试，不适合生产环境的持久化数据

### 数据持久化
如需持久化数据，建议：
1. 使用外部数据库（如MongoDB Atlas）
2. 使用Vercel KV存储
3. 集成第三方存储服务

## 🔄 自动部署

每次推送到GitHub main分支，Vercel会自动重新部署：
```bash
git add .
git commit -m "更新功能"
git push origin main
```

## 🐛 常见问题

### 1. 构建失败
- 检查 `requirements.txt` 格式
- 确保Python版本兼容

### 2. 静态文件404
- 确保静态文件在 `web/static/` 目录
- 检查文件路径是否正确

### 3. 数据丢失
- Vercel是无服务器环境，数据不持久化
- 每次冷启动会重置数据

## 📱 移动端适配

部署后的网站自动支持移动端访问，响应式设计确保在手机上也能正常使用。