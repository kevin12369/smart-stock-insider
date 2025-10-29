# 智股通项目 .gitignore 配置说明

本文档详细说明了智股通项目 `.gitignore` 文件中各个过滤规则的用途和重要性。

## 📋 目录

1. [基础开发环境](#基础开发环境)
2. [项目特定规则](#项目特定规则)
3. [安全与隐私](#安全与隐私)
4. [构建与部署](#构建与部署)
5. [工具与缓存](#工具与缓存)
6. [系统与编辑器](#系统与编辑器)

---

## 基础开发环境

### Python相关
```gitignore
# Python虚拟环境
venv/
env/
ENV/
.venv/

# Python编译文件
__pycache__/
*.py[cod]
*$py.class

# Python包管理
Pipfile.lock
.python-version
```
**用途**: 避免将虚拟环境、编译文件和锁文件提交到版本控制，这些文件在不同开发者的环境中会有差异。

### Node.js相关
```gitignore
# Node.js依赖
node_modules/

# 包管理器日志
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# 构建输出
dist/
dist-ssr/
build/
```
**用途**: `node_modules/` 体积巨大且可通过 `npm install` 重新生成，构建产物是临时的。

---

## 项目特定规则

### 测试相关 ⚡
```gitignore
# 测试结果和报告
tests/results/
tests/reports/*.html
tests/reports/*.json
tests/reports/*.csv
tests/performance/results/
tests/performance/reports/
tests/e2e/test-results/
tests/e2e/playwright-report/
tests/e2e/.playwright/

# 性能测试日志
performance_tests.log
locust_performance.log
```
**用途**: 测试产生的结果文件、报告和日志是临时的，每次测试都会重新生成，不需要版本控制。

### AI模型和数据文件 🤖
```gitignore
# AI模型文件
models/
*.pkl
*.joblib
*.h5
*.pb
*.onnx
*.model

# 数据集和缓存
data/datasets/
data/raw/
data/processed/
data/cache/
ai_cache/
model_cache/
```
**用途**: AI模型文件通常很大（MB到GB级别），数据集可能有版权限制，这些应该通过其他方式管理。

### 股票数据缓存 📈
```gitignore
# 股票数据缓存
stock_data/
market_data/
cache/stocks/
cache/market/
cache/analysis/
*.csv.gz
*.parquet
*.feather
```
**用途**: 股票数据缓存文件体积大且经常更新，应该从API实时获取，不应存储在版本控制中。

### 用户数据（保护隐私）🔒
```gitignore
# 用户隐私数据
user_data/
user_preferences/
portfolios/
watchlists/
user_profiles/
analytics_data/
```
**用途**: **极其重要** - 用户数据包含敏感个人信息，绝对不能提交到版本控制系统。

---

## 安全与隐私

### 配置文件和密钥 🔐
```gitignore
# 环境变量
.env.*
!.env.example

# 敏感配置
config/local.json
config/staging.json
config/production.json
config/secrets/
config/api_keys/
config/database/

# 证书和密钥
*.pem
*.key
*.crt
*.p12
*.pfx
secrets/
private_keys/
certificates/
ssl/
```
**用途**: **关键安全规则** - 防止API密钥、数据库密码、证书等敏感信息泄露到代码仓库。

### 日志文件 📝
```gitignore
# 详细日志过滤
logs/
*.log
access.log
error.log
debug.log
application.log
server.log
client.log
performance.log
security.log
audit.log
```
**用途**: 日志文件可能包含敏感信息，且会不断增长，不应版本控制。

---

## 构建与部署

### 构建产物 🏗️
```gitignore
# 前端构建
dist/
build/
target/
out/
.next/
.nuxt/

# 后端构建
.terraform/
.ansible/

# 文档构建
docs/generated/
docs/_build/
docs/.doctrees/
site/
public/
```
**用途**: 所有构建产物都是临时的，可以通过源代码重新生成。

### Docker相关 🐳
```gitignore
# Docker配置
docker-compose.override.yml
docker-compose.prod.yml
docker-compose.dev.yml
```
**用途**: 本地Docker配置可能包含敏感信息或特定环境设置。

---

## 工具与缓存

### 开发工具 🛠️
```gitignore
# IDE配置
.vscode/
.idea/
*.swp
*.swo
*~

# 缓存文件
.cache/
.parcel-cache/
.vite/
.eslintcache
.stylelintcache
.tsbuildinfo

# 测试工具
.pytest_cache/
.coverage
htmlcov/
.tox/
.nyc_output
coverage/
*.lcov
```
**用途**: 开发工具的配置和缓存文件因开发者而异，应该忽略。

### 系统文件 💻
```gitignore
# macOS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes

# Windows
ehthumbs.db
Thumbs.db
desktop.ini
```
**用途**: 操作系统生成的元数据文件，对项目开发无意义。

---

## 智股通特定补充规则

### 机器学习相关 🧠
```gitignore
# 训练数据和检查点
training_data/
model_checkpoints/
tensorboard_logs/
wandb/

# 数据可视化
charts/
graphs/
plots/
*.png.temp
*.svg.temp
```
**用途**: ML训练过程产生的文件通常很大且是临时的。

### 实时数据处理 📊
```gitignore
# 实时数据流
stream_data/
real_time_data/
websocket_logs/

# 性能监控
monitoring/
metrics/
traces/
*.prof
*.pprof
*.heap
```
**用途**: 实时数据和性能监控文件是动态生成的。

### 第三方服务 🌐
```gitignore
# 云服务配置
.aws/
.azure/
.gcp/
.firebase/

# 第三方集成
third_party/
external_services/
vendor/
```
**用途**: 第三方服务的配置文件可能包含敏感信息。

---

## ⚠️ 重要注意事项

### 1. 安全第一
- **绝对不要**提交任何包含API密钥、密码或证书的文件
- **绝对不要**提交包含用户个人信息的文件
- 使用环境变量和配置模板（如 `.env.example`）

### 2. 性能考虑
- 大文件（>50MB）应该考虑使用 Git LFS
- 避免提交二进制文件和压缩包
- 定期清理仓库中的不必要文件

### 3. 团队协作
- 确保所有团队成员都理解忽略规则
- 定期检查是否有重要文件被意外忽略
- 维护一个清晰的 `.env.example` 文件

### 4. 特殊情况
如果某些被忽略的文件确实需要版本控制：
1. 使用 `git add -f <file>` 强制添加
2. 考虑是否应该调整忽略规则
3. 确保不违反安全政策

---

## 📝 建议的最佳实践

1. **定期审查**: 定期检查 `.gitignore` 文件是否需要更新
2. **文档维护**: 保持本说明文档与实际配置同步
3. **安全检查**: 使用 `git-secrets` 等工具防止敏感信息泄露
4. **大文件处理**: 考虑使用 Git LFS 管理大文件
5. **模板文件**: 为所有配置文件提供安全的示例模板

---

**最后更新**: 2025-10-29
**维护者**: 智股通开发团队
**版本**: v1.0