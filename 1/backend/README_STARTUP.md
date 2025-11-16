# 后端服务启动指南

## 🚀 快速启动（开发环境）

### 方式1：自动启动（推荐）
直接运行游戏主程序，后端服务会自动启动：
```bash
cd 1
python main.py
```

### 方式2：手动启动
如果需要单独启动后端服务：
```bash
cd 1/backend
python start_server.py
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 📦 依赖安装

### 必需步骤（只需执行一次）

```bash
# 进入后端目录
cd 1/backend

# 安装所有依赖
pip install -r ../requirements.txt

# 或者使用一键安装脚本（Windows）
cd ..
install_backend_deps.bat
```

### 依赖列表
- `fastapi` - Web框架
- `uvicorn` - ASGI服务器
- `sqlalchemy` - ORM框架
- `passlib[bcrypt]` - 密码加密
- `python-jose[cryptography]` - JWT令牌
- `pydantic` - 数据验证
- `python-multipart` - 表单处理
- `python-dotenv` - 环境变量（可选）
- `requests` - HTTP客户端

---

## ⚙️ 配置说明

### 开发环境（默认，无需配置）

项目默认使用 **SQLite** 数据库，**无需任何配置**即可运行：
- ✅ 数据库自动创建：`card_game.db`
- ✅ 表结构自动初始化
- ✅ 初始数据自动加载

### 生产环境（可选配置）

如果需要使用 PostgreSQL 或自定义配置，创建 `.env` 文件：

```bash
cd 1/backend
# 创建 .env 文件（可选）
```

`.env` 文件内容示例：
```env
# 数据库配置（可选，默认使用SQLite）
DATABASE_URL=sqlite:///./card_game.db
# 或使用PostgreSQL：
# DATABASE_URL=postgresql://用户名:密码@localhost:5432/card_game_db

# JWT配置（可选，有默认值）
JWT_SECRET_KEY=你的随机密钥（建议使用 openssl rand -hex 32 生成）
```

**注意**：
- 开发环境**不需要**创建 `.env` 文件
- 只有使用 PostgreSQL 或需要自定义 JWT 密钥时才需要

---

## 🗄️ 数据库说明

### SQLite（默认，推荐用于开发）
- ✅ 无需安装数据库服务器
- ✅ 数据库文件：`1/backend/card_game.db`
- ✅ 自动创建和初始化
- ✅ 无需手动配置

### PostgreSQL（可选，用于生产）
如果使用 PostgreSQL：
1. 安装 PostgreSQL
2. 创建数据库：`CREATE DATABASE card_game_db;`
3. 在 `.env` 中配置 `DATABASE_URL`
4. 安装 PostgreSQL 驱动：`pip install psycopg2-binary`

---

## 🔍 常见问题

### 1. 后端服务启动失败

**问题**：`ModuleNotFoundError: No module named 'dotenv'`
**解决**：
```bash
pip install python-dotenv
```

**问题**：端口8000被占用
**解决**：
- 关闭占用端口的程序
- 或修改 `start_server.py` 中的端口号

### 2. 数据库错误

**问题**：数据库文件权限错误
**解决**：确保 `backend` 目录有写入权限

**问题**：表不存在
**解决**：删除 `card_game.db`，重新启动服务（会自动创建）

### 3. 依赖安装失败

**问题**：某些包安装失败
**解决**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 逐个安装
pip install fastapi uvicorn sqlalchemy
```

---

## 📝 测试接口

### 使用 Swagger UI（推荐）
1. 启动后端服务
2. 访问 http://localhost:8000/docs
3. 在页面上直接测试所有接口

### 使用命令行
```bash
# 健康检查
curl http://localhost:8000/health

# 用户注册
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 用户登录
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

---

## ✅ 检查清单

启动前确认：
- [ ] Python 3.8+ 已安装
- [ ] 所有依赖已安装（运行 `pip list` 检查）
- [ ] 端口8000未被占用
- [ ] `backend` 目录有写入权限（用于创建数据库）

启动后检查：
- [ ] 访问 http://localhost:8000/health 返回正常
- [ ] 访问 http://localhost:8000/docs 可以看到API文档
- [ ] `card_game.db` 文件已创建

---

## 🎮 与游戏集成

游戏主程序会自动：
1. ✅ 检测后端目录
2. ✅ 启动后端服务
3. ✅ 等待服务就绪
4. ✅ 显示启动状态

如果自动启动失败，会显示详细错误信息，按照提示解决即可。

