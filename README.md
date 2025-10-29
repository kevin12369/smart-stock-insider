# 智股通 (Smart Stock Insider) - AI增强轻量化专业版

<div align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Status-Stable-green.svg" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Desktop-blue.svg" alt="Platform">
</div>

<div align="center">
  <h3>🤖 AI驱动的专业股票分析平台 | AI-Powered Professional Stock Analysis Platform</h3>
  <p>专家圆桌系统 + GLM-4.5-Flash AI + 真实数据 | Expert Roundtable + GLM-4.5-Flash AI + Real Data</p>
</div>

> 基于GLM-4.5-Flash的专业桌面股票分析应用，为进阶投资者提供AI增强的投资研究服务 / Professional desktop stock analysis application powered by GLM-4.5-Flash, providing AI-enhanced investment research services for advanced investors

## 🎯 项目概述 / Project Overview

智股通AI增强轻量化专业版是一个专为个人进阶投资者设计的桌面股票分析应用。本版本采用GLM-4.5-Flash AI模型驱动的专家圆桌系统，提供专业级的股票分析和投资建议。

Smart Stock Insider AI Enhanced Lite Edition is a desktop stock analysis application designed for advanced individual investors. This version features an expert roundtable system driven by GLM-4.5-Flash AI model, providing professional-grade stock analysis and investment recommendations.

### ✨ 核心功能 / Core Features

#### 🤖 GLM-4.5-Flash专家圆桌系统 / GLM-4.5-Flash Expert Roundtable System
- **技术面分析师**: 15年技术分析经验，专注技术指标、K线形态和趋势分析
- **基本面分析师**: 专业财务分析背景，精通估值模型和行业分析
- **新闻分析师**: 资深财经记者背景，擅长新闻情感分析和事件解读
- **风控分析师**: 专业风险管理师，专注投资风险控制和仓位管理
- **智能意见整合**: 加权算法整合专家观点，生成最终投资建议
- **置信度评估**: 透明的分析置信度评分，辅助投资决策

- **Technical Analyst**: 15 years of technical analysis experience, focusing on technical indicators, candlestick patterns, and trend analysis
- **Fundamental Analyst**: Professional financial analysis background, expert in valuation models and industry analysis
- **News Analyst**: Senior financial journalist background, skilled in sentiment analysis and event interpretation
- **Risk Analyst**: Professional risk manager, focusing on investment risk control and position management
- **Intelligent Opinion Integration**: Weighted algorithm integrates expert opinions to generate final investment recommendations
- **Confidence Assessment**: Transparent analysis confidence scoring to support investment decisions

#### 📊 真实股票数据 / Real Stock Data
- **AKShare集成**: 实时获取A股、港股、美股市场数据
- **技术指标计算**: MACD、KDJ、RSI、布林带等专业指标
- **历史数据回溯**: 支持任意时间段的历史数据查询
- **无模拟数据**: 坚持使用真实市场数据，避免投资误导

- **AKShare Integration**: Real-time data from A-shares, Hong Kong stocks, and US markets
- **Technical Indicator Calculation**: MACD, KDJ, RSI, Bollinger Bands, and other professional indicators
- **Historical Data Backtracking**: Support for historical data queries of any time period
- **No Simulated Data**: Commitment to real market data only, avoiding investment misinformation

#### 🔄 专业级错误处理 / Professional Error Handling
- **网络问题处理**: 404风格错误响应，提示用户稍后重试
- **数据源保护**: 优雅降级，确保系统稳定性
- **透明错误报告**: 详细的错误信息和建议操作
- **投资者保护**: 绝不提供误导性虚假数据

- **Network Issue Handling**: 404-style error responses prompting users to retry later
- **Data Source Protection**: Graceful degradation ensuring system stability
- **Transparent Error Reporting**: Detailed error information and recommended actions
- **Investor Protection**: Never provides misleading false data

## 🏗️ 系统架构

```
智股通AI增强轻量化架构
┌─────────────────────────────────────────────────────────┐
│                    前端 (Frontend)                      │
│  React 18 + TypeScript + Ant Design + Tailwind CSS      │
│                      ↕️ HTTP/API                        │
├─────────────────────────────────────────────────────────┤
│                  后端 (Backend)                         │
│         FastAPI + Python 3.12 + GLM-4.5-Flash           │
│                      ↕️ 微服务调用                       │
├─────────────────────────────────────────────────────────┤
│                核心服务 (Core Services)                  │
│  ┌─────────────┬──────────────┬─────────────────────────┐ │
│  │  数据服务    │   AI分析服务   │      专家圆桌协调器      │ │
│  │ Data Service │ AI Analysis   │ RoundTable Coordinator │ │
│  │  (AKShare)   │ (GLM-4.5)     │    (Expert System)     │ │
│  └─────────────┴──────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- **Python**: >= 3.12
- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0
- **Git**: 最新版本 / Latest version

### 安装步骤 / Installation

1. **克隆仓库 / Clone Repository**
```bash
git clone https://github.com/kevin12369/smart-stock-insider.git
cd smart-stock-insider
```

2. **创建虚拟环境 / Create Virtual Environment**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. **安装后端依赖 / Install Backend Dependencies**
```bash
pip install -r requirements-final.txt
```

4. **安装前端依赖 / Install Frontend Dependencies**
```bash
cd frontend
npm install
cd ..
```

5. **配置环境变量 / Configure Environment Variables**
```bash
cp .env.example .env
# 编辑 .env 文件，配置GLM API密钥
# Edit .env file to configure GLM API key
```

### 启动应用 / Launch Application

1. **启动后端服务 / Start Backend Service**
```bash
cd backend
python main_standalone.py
```

2. **启动前端开发服务器 / Start Frontend Dev Server**
```bash
cd frontend
npm run dev
```

3. **访问应用 / Access Application**
- 前端界面: http://localhost:10001
- 后端API: http://localhost:8001
- API文档: http://localhost:8001/docs

## 🔧 配置说明 / Configuration

### GLM-4.5-Flash AI配置 / GLM-4.5-Flash AI Configuration
```env
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
GLM_MODEL=glm-4.5-flash
GLM_MAX_TOKENS=96000
```

### 数据服务配置 / Data Service Configuration
```env
AKSHARE_ENABLED=true
DATA_CACHE_TIMEOUT=300
STOCK_DATA_RETRY_COUNT=3
```

## 🎨 功能特色 / Features

### 🔍 专家圆桌分析 / Expert Roundtable Analysis
- **四位AI专家协作**: 技术面、基本面、新闻面、风控面全面分析
- **实时会议模拟**: 并行分析 + 智能意见整合
- **置信度评分**: 透明的分析可信度评估
- **投资建议**: 基于专家共识的综合建议

### 📈 智能股票分析 / Intelligent Stock Analysis
- **实时数据**: AKShare提供的高质量市场数据
- **技术指标**: 完整的技术分析工具集
- **趋势识别**: AI驱动的趋势预测和信号识别
- **风险评估**: 专业的投资风险量化分析

### 🛡️ 投资者保护 / Investor Protection
- **真实数据优先**: 绝不使用模拟数据误导投资者
- **透明错误处理**: 网络问题时提供清晰的错误信息
- **风险提示**: 明确标识数据获取状态
- **专业标准**: 遵循金融服务的专业规范

## 📖 详细文档 / Documentation

完整的项目文档已整理到 `docs/` 目录：

- [📚 文档索引](./docs/DOCUMENTATION_INDEX.md) - 完整的文档导航
- [🏗️ 架构设计](./docs/architecture/ARCHITECTURE.md) - 系统架构文档
- [📊 修复报告](./docs/reports/) - 完整的开发和修复历程
- [📖 操作指南](./docs/guides/) - 项目操作指南

## 🧪 测试 / Testing

```bash
# 运行后端测试 / Run Backend Tests
cd backend
python -m pytest tests/

# 运行前端测试 / Run Frontend Tests
cd frontend
npm test

# 运行集成测试 / Run Integration Tests
npm run test:integration
```

## 📦 构建 / Build

```bash
# 构建前端 / Build Frontend
cd frontend
npm run build

# 构建桌面应用 / Build Desktop Application
npm run tauri:build

# 构建Docker镜像 / Build Docker Image
docker-compose build
```

## 🤝 贡献指南 / Contributing

我们欢迎所有形式的贡献！请阅读 [贡献指南](./docs/DEVELOPMENT_GUIDELINES.md) 了解详细信息。

### 开发流程 / Development Flow

1. Fork 项目 / Fork the project
2. 创建功能分支 / Create feature branch (`git checkout -b feature/amazing-feature`)
3. 提交更改 / Commit changes (`git commit -m 'Add amazing feature'`)
4. 推送到分支 / Push to branch (`git push origin feature/amazing-feature`)
5. 创建 Pull Request / Create Pull Request

## 📊 项目状态 / Project Status

### ✅ 已完成功能 / Completed Features
- [x] **GLM-4.5-Flash AI集成**: 专家圆桌系统完全实现
- [x] **真实股票数据服务**: AKShare数据集成，无模拟数据
- [x] **专业错误处理**: 404风格错误响应，投资者保护
- [x] **前端界面优化**: React + Ant Design现代化界面
- [x] **后端API服务**: FastAPI高性能API接口
- [x] **项目文档整理**: 完整的技术文档体系

### 🚀 核心技术栈 / Core Tech Stack

**后端 / Backend**:
- Python 3.12 + FastAPI
- GLM-4.5-Flash AI Integration
- AKShare Real-time Data
- Expert Roundtable System

**前端 / Frontend**:
- React 18 + TypeScript 5.2
- Ant Design 5.12.8
- Tailwind CSS 3.3.6
- Vite 5.0.8 Build Tool

**AI服务 / AI Services**:
- GLM-4.5-Flash (128K Context, 96K Output)
- 4 Expert Analysts
- Intelligent Opinion Integration
- Confidence Assessment

### 📈 当前版本 / Current Version
**Version**: 1.0.0
**Status**: 🟢 Stable - Production Ready
**Last Update**: 2025-10-29

## 🎯 核心优势 / Key Advantages

### 🤖 AI驱动分析
- GLM-4.5-Flash大模型提供专业级分析能力
- 四位AI专家协同工作，覆盖投资分析全维度
- 智能意见整合算法，生成高质量投资建议

### 📊 真实数据保障
- 坚持使用真实市场数据，绝不提供模拟数据
- AKShare提供高质量、实时的股票数据
- 专业的错误处理机制，避免投资误导

### 🛡️ 投资者保护
- 透明的数据状态标识
- 清晰的错误提示和建议
- 符合金融服务的专业标准

## 🙏 致谢 / Acknowledgments

- [GLM-4.5-Flash](https://open.bigmodel.cn/) - 强大的AI分析能力
- [AKShare](https://www.akshare.xyz/) - 专业的金融数据接口
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [React](https://reactjs.org/) - 用户界面构建库
- [Ant Design](https://ant.design/) - 企业级UI设计语言

## 📞 联系方式 / Contact

- **项目维护者 / Project Maintainer**: Kevin
- **邮箱 / Email**: kyd96321@gmail.com
- **GitHub**: https://github.com/kevin12369/smart-stock-insider
- **问题反馈 / Issues**: https://github.com/kevin12369/smart-stock-insider/issues

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，请给我们一个星标！ / If this project helps you, please give us a star!</p>
  <p>🎯 专为进阶投资者打造的专业AI分析工具 / Professional AI Analysis Tool for Advanced Investors</p>
  <p>Made with ❤️ by Smart Stock Insider Team</p>
</div>