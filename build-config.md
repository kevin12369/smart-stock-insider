# 智股通项目打包配置规范

## 📦 打包命名规则

### 命名格式
```
项目缩写-系统-支持的架构-版本号
```

### 具体规范
- **项目缩写**: `ssi` (Smart Stock Insider)
- **系统**: `windows` / `linux` / `macos`
- **支持的架构**: `amd64` / `arm64`
- **版本号**: `v0.0.1-dev` (内测阶段)

### 打包文件命名示例
```
ssi-windows-amd64-v0.0.1-dev.exe     # Windows 64位
ssi-linux-amd64-v0.0.1-dev          # Linux 64位
ssi-macos-amd64-v0.0.1-dev          # macOS Intel 64位
ssi-macos-arm64-v0.0.1-dev          # macOS Apple Silicon
```

## 🏗️ 构建配置

### 版本管理
- **开发阶段**: v0.0.1-dev (内测)
- **测试阶段**: v0.1.0-beta (公测)
- **正式发布**: v1.0.0 (正式版)

### 构建脚本
```bash
#!/bin/bash
# build.sh - 标准化构建脚本

set -e

# 配置变量
PROJECT_NAME="ssi"
SYSTEM="windows"
ARCH="amd64"
VERSION="v0.0.1-dev"
OUTPUT_NAME="${PROJECT_NAME}-${SYSTEM}-${ARCH}-${VERSION}"

# 清理旧文件
echo "清理旧的构建文件..."
rm -f *.exe

# 构建应用
echo "开始构建应用..."
wails build -clean -upx

# 重命名文件
echo "重命名构建文件..."
mv build/bin/smart-stock-insider.exe "${OUTPUT_NAME}.exe"

# 生成校验和
echo "生成文件校验和..."
sha256sum "${OUTPUT_NAME}.exe" > "${OUTPUT_NAME}.exe.sha256"

echo "构建完成！"
echo "文件名: ${OUTPUT_NAME}.exe"
echo "校验和: ${OUTPUT_NAME}.exe.sha256"
```

### 安装包配置
```json
{
  "name": "智股通",
  "shortname": "ssi",
  "version": "0.0.1-dev",
  "description": "智能投研平台",
  "author": "Smart Stock Team",
  "homepage": "https://smart-stock.example.com",
  "nsis": {
    "displayName": "智股通 v0.0.1-dev",
    "license": "LICENSE",
    "oneclick": false,
    "allowToChangeInstallationDirectory": true,
    "installIcon": "./assets/icon.ico",
    "uninstallIcon": "./assets/icon.ico"
  }
}
```

## 🚀 发布流程

### 1. 预发布检查
- [ ] 代码审查完成
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 安全扫描通过

### 2. 构建打包
```bash
# 1. 更新版本号
echo "v0.0.1-dev" > VERSION

# 2. 运行构建脚本
./build.sh

# 3. 生成发布包
wails build -nsis
```

### 3. 质量检查
- [ ] 文件完整性检查
- [ ] 病毒扫描
- [ ] 安装测试
- [ ] 功能测试

### 4. 发布准备
- [ ] 更新CHANGELOG.md
- [ ] 生成发布说明
- [ ] 创建发布标签
- [ ] 上传到发布平台

## 📋 版本控制

### 版本号规则
- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正
- **后缀**: `-dev` (开发), `-beta` (测试), `-rc` (候选)

### 分支管理
- **main**: 主分支，稳定版本
- **develop**: 开发分支，最新功能
- **feature/***: 功能分支
- **release/***: 发布分支
- **hotfix/***: 热修复分支

## 🔧 开发环境配置

### 本地开发
```bash
# 1. 克隆仓库
git clone https://github.com/smart-stock/ssi.git
cd ssi

# 2. 安装依赖
go mod download
cd frontend && npm install && cd ..

# 3. 开发模式运行
wails dev
```

### 调试模式
```bash
# 生成调试版本
wails build -debug

# 运行调试
./ssi-windows-amd64-debug.exe
```

## 📊 构建统计

### 文件大小
- **调试版本**: ~45MB
- **发布版本**: ~30MB (UPX压缩)
- **安装包**: ~35MB

### 构建时间
- **前端构建**: 2-3分钟
- **后端构建**: 1-2分钟
- **打包压缩**: 30秒
- **总计**: 4-6分钟

## 🔒 安全配置

### 代码签名
```bash
# Windows代码签名 (需要证书)
signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com ssi-windows-amd64-v0.0.1-dev.exe

# macOS代码签名 (需要开发者证书)
codesign --sign "Developer ID Application" ssi-macos-amd64-v0.0.1-dev.app
```

### 安全检查
```bash
# 病毒扫描
clamscan ssi-windows-amd64-v0.0.1-dev.exe

# 依赖漏洞检查
go list -json -m all | nancy sleuth
```

## 📝 发布说明模板

### 版本发布说明
```
# 智股通 v0.0.1-dev 发布说明

## 🎯 版本信息
- 版本号: v0.0.1-dev
- 发布日期: 2024-10-24
- 系统支持: Windows 10/11 (64位)

## ✨ 新增功能
- 技术信号量化系统 (30个技术指标)
- 多角色AI助手系统
- 智能新闻聚合系统
- 投资组合管理功能
- 实时推送通知服务

## 🐛 修复问题
- 修复SQLite数据库连接问题
- 优化内存使用性能
- 修复前端显示bug

## ⚠️ 注意事项
- 本版本为内测版本，仅供测试使用
- 数据仅供参考，不构成投资建议
- 请勿在生产环境中使用

## 📦 下载地址
- Windows版: [ssi-windows-amd64-v0.0.1-dev.exe]
- 校验和: [ssi-windows-amd64-v0.0.1-dev.exe.sha256]

## 📞 反馈渠道
- 问题反馈: https://github.com/smart-stock/ssi/issues
- 邮件联系: support@smart-stock.example.com
```

---

*最后更新: 2024-10-24*