# 校园二手交易平台

一个基于Django的校园二手交易平台，为学生提供便捷的二手物品交易服务。

## 功能特性

### 核心功能
- **用户注册登录** - 支持用户注册和登录
- **商品发布** - 用户可以发布二手商品信息
- **商品浏览** - 浏览所有可用的二手商品
- **商品搜索** - 支持关键词搜索和分类筛选
- **商品收藏** - 用户可以收藏感兴趣的商品
- **消息系统** - 买家和卖家可以通过平台进行沟通
- **评价系统** - 交易完成后可以对卖家进行评价

### 技术特性
- 基于Django 3.2.25框架开发
- 使用SQLite数据库（可扩展至MySQL/PostgreSQL）
- 响应式设计，支持移动端访问
- 使用Bootstrap 5进行前端美化
- 支持图片上传和显示
- 中文界面，符合国内用户习惯

## 安装和运行

### 环境要求
- Python 3.7+
- Django 3.2.25
- Pillow（图片处理库）

### 安装步骤

1. 克隆或下载项目代码
2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   ```

3. 激活虚拟环境：
   - Windows: `.venv\Scripts\Activate.ps1`
   - Linux/Mac: `source .venv/bin/activate`

4. 安装依赖：
   ```bash
   pip install django==3.2.25 pillow
   ```

5. 进入项目目录：
   ```bash
   cd demo
   ```

6. 创建数据库迁移：
   ```bash
   python manage.py makemigrations marketplace
   ```

7. 应用数据库迁移：
   ```bash
   python manage.py migrate
   ```

8. 创建超级用户（可选）：
   ```bash
   python manage.py createsuperuser
   ```

9. 启动开发服务器：
   ```bash
   python manage.py runserver
   ```

10. 访问应用：
    - 网站首页：http://127.0.0.1:8000/
    - 管理后台：http://127.0.0.1:8000/admin/

## 项目结构

```
demo/
├── demo/                 # 主项目配置
│   ├── settings.py       # 项目设置
│   ├── urls.py          # 主URL路由
│   └── ...
├── marketplace/         # 主要应用
│   ├── models.py        # 数据模型
│   ├── views.py         # 视图函数
│   ├── urls.py          # 应用URL路由
│   ├── forms.py         # 表单定义
│   ├── admin.py         # 管理后台配置
│   └── templates/       # 模板文件
├── templates/           # 基础模板
│   └── base.html       # 基础模板
├── static/             # 静态文件
│   └── css/           # CSS样式
├── media/             # 媒体文件（用户上传）
└── db.sqlite3         # SQLite数据库
```

## 数据模型

### 主要模型
- **Category** - 商品分类
- **Product** - 二手商品信息
- **Favorite** - 用户收藏
- **Message** - 用户消息
- **Review** - 用户评价

## 使用说明

### 普通用户
1. 注册账号并登录
2. 浏览首页查看最新和热门商品
3. 使用搜索功能查找特定商品
4. 点击商品查看详细信息
5. 可以收藏商品或联系卖家
6. 发布自己的二手商品

### 卖家用户
1. 登录后可以发布商品
2. 管理已发布的商品
3. 回复买家消息
4. 查看收到的评价

### 管理员
1. 访问/admin/进入管理后台
2. 管理用户、商品、分类等数据
3. 监控平台运行状态

## 开发说明

### 添加新功能
1. 在`marketplace/models.py`中定义数据模型
2. 运行`python manage.py makemigrations`创建迁移
3. 运行`python manage.py migrate`应用迁移
4. 在`marketplace/views.py`中添加视图函数
5. 在`marketplace/urls.py`中配置URL路由
6. 在`templates/marketplace/`中创建模板文件

### 自定义样式
- 主要样式文件：`static/css/style.css`
- 基础模板：`templates/base.html`
- 使用Bootstrap 5类名进行样式调整

## 部署说明

### 生产环境部署
1. 修改`settings.py`中的DEBUG为False
2. 设置ALLOWED_HOSTS为实际域名
3. 配置数据库（推荐使用MySQL或PostgreSQL）
4. 配置静态文件和媒体文件服务
5. 使用WSGI服务器（如Gunicorn）部署
6. 配置反向代理（如Nginx）

### 安全配置
- 设置SECRET_KEY环境变量
- 配置HTTPS
- 设置合适的数据库权限
- 定期备份数据

## 许可证

本项目仅用于学习和演示目的。

## 联系方式

如有问题或建议，请联系开发者。