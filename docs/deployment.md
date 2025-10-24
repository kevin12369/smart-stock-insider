# 智股通部署指南

## 概述

智股通是一个基于Wails v2框架的桌面应用，结合Go后端和React前端，提供智能量化投研服务。

## 系统要求

### 开发环境要求
- Go 1.24+
- Node.js 18+
- Python 3.9+ (可选，用于AI分析)
- Git

### 生产环境要求
- Windows 10/11, macOS 10.15+, 或 Linux (Ubuntu 20.04+)
- 至少 4GB RAM
- 至少 2GB 可用磁盘空间

## 构建部署

### 1. 环境准备

#### Windows 环境
```bash
# 安装Go
# 从 https://golang.org/dl/ 下载并安装

# 安装Node.js
# 从 https://nodejs.org/ 下载并安装

# 安装Wails CLI
go install github.com/wailsapp/wails/v2/cmd/wails@latest

# 安装依赖
npm install -g @wailsapp/cli
```

#### macOS/Linux 环境
```bash
# 安装Go
wget https://go.dev/dl/go1.24.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.24.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装Wails
go install github.com/wailsapp/wails/v2/cmd/wails@latest
```

### 2. 项目构建

#### 开发模式构建
```bash
# 克隆项目
git clone <repository-url>
cd smart-stock-insider

# 安装前端依赖
cd frontend
npm install
cd ..

# 安装Go依赖
go mod tidy

# 运行开发模式
wails dev
```

#### 生产模式构建
```bash
# 构建前端
cd frontend
npm run build
cd ..

# 构建桌面应用
wails build
```

### 3. 构建脚本

项目提供了自动化构建脚本：

```bash
# Windows
./scripts/build-windows.bat

# macOS/Linux
chmod +x ./scripts/build-unix.sh
./scripts/build-unix.sh
```

## 部署配置

### 1. 环境变量配置

创建 `.env` 文件：
```env
# 应用配置
APP_NAME=智股通
APP_VERSION=1.0.0
APP_ENV=production

# 数据库配置
DB_PATH=./data/smart_stock.db
DB_BACKUP_PATH=./backups

# API配置
API_HOST=localhost
API_PORT=8080
API_CORS_ORIGIN=http://localhost:3000

# 数据源配置
AKSHARE_ENABLED=true
NEWS_SOURCES=eastmoney,tonghuashun,sina,tencent

# 缓存配置
CACHE_SIZE=1000
CACHE_TTL=300

# 日志配置
LOG_LEVEL=info
LOG_FILE=./logs/app.log
```

### 2. 数据库配置

#### SQLite配置
- 默认使用现代SQLite驱动 (modernc.org/sqlite)
- 数据库文件位置: `./data/smart_stock.db`
- 自动创建表结构和索引

#### 备份策略
```bash
# 每日备份脚本
./scripts/backup-database.sh

# 恢复备份
./scripts/restore-database.sh backup_20241201.db
```

### 3. 性能优化配置

#### 缓存配置
```go
// 缓存服务配置
cacheConfig := &cache.CacheConfig{
    MaxSize:    1000,
    DefaultTTL: 5 * time.Minute,
    CleanupInterval: 1 * time.Minute,
}
```

#### 连接池配置
```go
// 数据库连接池
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(5 * time.Minute)
```

## 部署方式

### 1. 单机部署

#### Windows 部署
```bash
# 构建应用
wails build

# 运行应用
dist/smart-stock-insider.exe
```

#### macOS 部署
```bash
# 构建应用
wails build

# 创建应用包
./scripts/create-dmg.sh

# 安装应用
open dist/SmartStockInsider.dmg
```

#### Linux 部署
```bash
# 构建应用
wails build

# 创建AppImage
./scripts/create-appimage.sh

# 运行应用
./dist/SmartStockInsider.AppImage
```

### 2. 服务部署

作为后台服务运行：

#### Windows Service
```bash
# 安装服务
./scripts/install-service.bat

# 启动服务
net start SmartStockInsider

# 查看服务状态
sc query SmartStockInsider
```

#### systemd Service (Linux)
```bash
# 创建服务文件
sudo cp ./scripts/smart-stock-insider.service /etc/systemd/system/

# 启用并启动服务
sudo systemctl enable smart-stock-insider
sudo systemctl start smart-stock-insider

# 查看服务状态
sudo systemctl status smart-stock-insider
```

### 3. 容器部署

#### Docker构建
```dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM golang:1.24-alpine AS backend-builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=backend-builder /app/dist .
CMD ["./smart-stock-insider"]
```

```bash
# 构建Docker镜像
docker build -t smart-stock-insider .

# 运行容器
docker run -p 8080:8080 -v ./data:/app/data smart-stock-insider
```

## 监控和日志

### 1. 日志配置

#### 日志级别
- `debug`: 详细的调试信息
- `info`: 一般信息 (推荐生产环境)
- `warn`: 警告信息
- `error`: 错误信息

#### 日志轮转
```bash
# 日志轮转配置 /etc/logrotate.d/smart-stock-insider
./logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 app app
}
```

### 2. 性能监控

#### 应用指标
- 内存使用情况
- CPU使用率
- 请求响应时间
- 数据库查询性能
- 缓存命中率

#### 监控脚本
```bash
# 运行监控
./scripts/monitor.sh

# 查看性能指标
./scripts/performance-stats.sh
```

### 3. 健康检查

#### 健康检查端点
```
GET /api/health
```

响应示例：
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": {
      "connected": true,
      "query_time_ms": 12
    },
    "cache": {
      "hit_rate": 0.85,
      "size": 256
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 安全配置

### 1. 数据加密

#### 数据库加密
```bash
# 生成加密密钥
openssl rand -hex 32 > ./data/encryption.key
chmod 600 ./data/encryption.key
```

#### 敏感数据保护
- API密钥加密存储
- 用户数据本地加密
- 网络传输HTTPS

### 2. 访问控制

#### 防火墙配置
```bash
# 仅允许本地访问
iptables -A INPUT -p tcp --dport 8080 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

#### 数据源限制
- API调用频率限制
- 数据源访问白名单
- 异常访问检测

## 故障排除

### 常见问题

#### 1. 构建失败
```bash
# 清理依赖
go clean -modcache
npm cache clean --force

# 重新安装
go mod tidy
npm install
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件权限
ls -la ./data/

# 检查SQLite版本
sqlite3 --version
```

#### 3. 应用启动失败
```bash
# 查看详细日志
export WAILS_LOG_LEVEL=debug
./smart-stock-insider

# 检查端口占用
netstat -tulpn | grep 8080
```

### 性能问题诊断

#### 1. 内存泄漏检测
```bash
# 使用pprof
go tool pprof http://localhost:8080/debug/pprof/heap
```

#### 2. 数据库性能分析
```sql
-- 查看慢查询
EXPLAIN QUERY PLAN SELECT * FROM stock_daily WHERE date = '2024-01-15';
```

#### 3. 网络延迟检测
```bash
# 测试数据源响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://api.akshare.example.com
```

## 版本管理

### 版本发布流程

1. 代码审查
2. 自动化测试
3. 构建生产版本
4. 创建发布标签
5. 生成更新包

### 自动更新

#### 检查更新
```bash
# 检查新版本
./scripts/check-updates.sh

# 自动更新
./scripts/auto-update.sh
```

## 维护和备份

### 定期维护任务

#### 数据库维护
```bash
# 每周执行
./scripts/maintenance.sh
```

#### 缓存清理
```bash
# 清理过期缓存
./scripts/cleanup-cache.sh
```

#### 日志归档
```bash
# 归档旧日志
./scripts/archive-logs.sh
```

### 备份策略

#### 自动备份
```bash
# 配置定时备份
crontab -e

# 每日凌晨2点备份
0 2 * * * /path/to/smart-stock-insider/scripts/backup-database.sh
```

#### 灾难恢复
1. 恢复数据库备份
2. 重新构建应用
3. 验证数据完整性
4. 恢复服务

## 技术支持

### 文档资源
- [API文档](./api-documentation.md)
- [用户手册](./user-manual.md)
- [开发者指南](./developer-guide.md)

### 社区支持
- GitHub Issues: 报告bug和功能请求
- Wiki: 详细文档和FAQ
- Discussions: 用户交流

### 联系方式
- 邮箱: support@smart-stock-insider.com
- 文档: https://docs.smart-stock-insider.com