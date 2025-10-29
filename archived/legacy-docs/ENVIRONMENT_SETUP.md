# 智股通项目环境配置指南

## 概述

本指南详细说明如何在 Python 3.12 环境下配置智股通项目开发环境。

## 系统要求

- **操作系统**: Windows 10+ / macOS 10.15+ / Linux
- **Python**: 3.12 或更高版本
- **Node.js**: 18.0.0 或更高版本
- **npm**: 9.0.0 或更高版本
- **Rust**: 1.70.0 或更高版本
- **Redis**: 6.0+ (需要运行中的Redis服务)

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd smart-stock-insider
```

### 2. Python环境配置

```bash
# 自动配置Python 3.12环境
python scripts/setup_python_env.py

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. 环境验证

```bash
# 验证环境配置
python scripts/verify_environment.py
```

### 4. 启动项目

```bash
# 启动完整项目（前端+后端）
npm run dev

# 或者分别启动：
# 后端:
cd backend && python main.py
# 前端:
cd frontend && npm run tauri dev
```

## 详细配置步骤

### Python 3.12 环境配置

#### 1. 检查Python版本

```bash
python --version
# 应显示: Python 3.12.x 或更高版本
```

#### 2. 创建虚拟环境

项目提供了自动配置脚本：

```bash
python scripts/setup_python_env.py
```

脚本将执行以下操作：
- 检查Python版本兼容性
- 创建`.venv`虚拟环境
- 升级pip到最新版本
- 安装Python 3.12兼容的依赖
- 创建环境配置文件

#### 3. 激活虚拟环境

**Windows:**
```cmd
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

#### 4. 手动安装依赖（可选）

如果自动安装失败，可以手动安装：

```bash
pip install -r requirements-312.txt
```

### 环境变量配置

创建`.env`文件（自动配置脚本已创建）：

```env
# 应用基础配置
ENVIRONMENT=development
DEBUG=true
APP_NAME=智股通
VERSION=1.0.0

# 服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=sqlite:///./data/smart_stock.db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# AI模型配置
GLM_API_KEY=your-glm-api-key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
GLM_MODEL=glm-4.5-flash
```

### Node.js 环境配置

#### 1. 安装Node.js

从 [Node.js官网](https://nodejs.org/) 下载并安装 Node.js 18+ 版本。

#### 2. 安装前端依赖

```bash
# 在项目根目录
npm install

# 或者在frontend目录
cd frontend
npm install
```

### Rust 环境配置

#### 1. 安装Rust

从 [Rust官网](https://rustup.rs/) 下载并安装 Rust。

#### 2. 验证安装

```bash
rustc --version
cargo --version
```

### Redis 服务配置

#### Windows

```cmd
# 使用Chocolatey安装
choco install redis-64

# 或下载Redis for Windows
# 启动Redis服务
redis-server
```

#### macOS

```bash
# 使用Homebrew安装
brew install redis

# 启动Redis服务
brew services start redis
```

#### Linux (Ubuntu/Debian)

```bash
# 安装Redis
sudo apt update
sudo apt install redis-server

# 启动Redis服务
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## 问题排查

### 常见问题及解决方案

#### 1. Python版本不兼容

**问题**: `❌ Python版本检查失败 - 需要: 3.12+`

**解决方案**:
- 安装Python 3.12+版本
- 从 [Python官网](https://www.python.org/downloads/) 下载

#### 2. Redis连接失败

**问题**: `❌ Redis连接检查失败`

**解决方案**:
- 确保Redis服务正在运行
- 检查Redis配置（主机、端口）
- Windows可能需要手动启动Redis服务

#### 3. 依赖安装失败

**问题**: `❌ 依赖安装失败`

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install -r requirements-312.txt --no-cache-dir
```

#### 4. Tauri编译失败

**问题**: Rust编译错误

**解决方案**:
```bash
# 更新Rust工具链
rustup update

# 清理Cargo缓存
cargo clean

# 重新构建
cd frontend && npm run tauri build
```

#### 5. 端口冲突

**问题**: `Port XXXX is already in use`

**解决方案**:
- 查找占用端口的进程：
  ```bash
  # Windows
  netstat -ano | findstr :8000

  # macOS/Linux
  lsof -i :8000
  ```
- 终止进程或更改配置中的端口号

#### 6. 虚拟环境问题

**问题**: 虚拟环境激活失败

**解决方案**:
```bash
# 删除现有虚拟环境
rm -rf .venv

# 重新创建
python scripts/setup_python_env.py
```

## 开发工作流

### 1. 日常开发

```bash
# 激活环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 启动项目
npm run dev
```

### 2. 代码质量检查

```bash
# Python代码格式化
black backend/
isort backend/

# TypeScript代码检查
cd frontend && npm run lint
```

### 3. 测试

```bash
# Python测试
pytest backend/

# 前端测试
cd frontend && npm test
```

## 项目结构

```
smart-stock-insider/
├── backend/                 # Python后端
│   ├── core/               # 核心配置
│   ├── api/                # API路由
│   ├── models/             # 数据模型
│   └── services/           # 业务服务
├── frontend/               # Tauri前端
│   ├── src/                # React源码
│   ├── src-tauri/          # Tauri配置
│   └── package.json        # Node.js依赖
├── scripts/                # 配置脚本
│   ├── setup_python_env.py # Python环境配置
│   └── verify_environment.py # 环境验证
├── docs/                   # 文档
├── requirements-312.txt    # Python 3.12依赖
└── .env                    # 环境变量
```

## 性能优化建议

### Python环境优化

1. **使用uv替代pip**（可选）:
   ```bash
   pip install uv
   uv pip install -r requirements-312.txt
   ```

2. **启用JIT编译**（PyPy）:
   ```bash
   # 安装PyPy并使用
   ```

### 开发环境优化

1. **SSD硬盘**: 提高I/O性能
2. **16GB+内存**: 处理大量数据
3. **多核CPU**: 并行处理能力

## 安全注意事项

1. **生产环境**:
   - 修改默认SECRET_KEY
   - 使用HTTPS
   - 配置防火墙

2. **API密钥**:
   - 不要提交到版本控制
   - 使用环境变量
   - 定期轮换

## 支持与反馈

如果遇到问题：

1. 查看本文档的问题排查部分
2. 运行环境验证脚本: `python scripts/verify_environment.py`
3. 查看项目日志
4. 提交Issue到项目仓库

---

**版本**: 1.0.0
**更新时间**: 2025-01-29
**维护者**: Smart Stock Insider Team