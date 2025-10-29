# 智股通项目删改优化方案

## 📋 问题诊断

### 🔴 当前项目状态
- **依赖包数量**: 160+ 个重型依赖
- **技术栈复杂**: Go + Python + Tauri + React 混合架构
- **Python 3.12兼容性**: torch, transformers, nltk, jieba 等库存在冲突
- **代码冗余**: 包含大量用户不需要的模型训练和复杂AI功能

### ❌ 需要删除的模块
1. **机器学习训练模块**
   - torch, transformers, scikit-learn
   - 模型训练脚本和配置
   - 复杂的深度学习依赖

2. **复杂数据处理模块**
   - polars, backtrader, empirical, pyfolio
   - 量化回测引擎
   - 高级统计计算库

3. **新闻抓取系统**
   - newspaper3k, playwright, beautifulsoup4
   - 复杂的NLP处理 (nltk, jieba)
   - 多源新闻聚合器

4. **重型数据库模块**
   - redis, hiredis, alembic
   - 复杂的数据库迁移系统
   - 缓存和任务队列 (celery, kombu)

5. **可视化和报告模块**
   - plotly, matplotlib, seaborn, mplfinance
   - 复杂的图表生成
   - wordcloud, fuzzywuzzy

## ✅ 保留的核心功能

### 🎯 用户需求明确
1. **桌面应用**: 针对 Python 3.12 优化
2. **AI增强**: 使用免费的 GLM-4.5-Flash API
3. **目标用户**: 个人进阶投资者
4. **数据要求**: 真实数据，拒绝模拟数据
5. **核心功能**: 专家圆桌会议系统

### 📦 保留的技术栈
1. **后端**: FastAPI + Python 3.12
2. **前端**: React + TypeScript + Ant Design
3. **数据**: akshare (真实股票数据)
4. **AI**: GLM-4.5-Flash API集成
5. **桌面**: Tauri 2.0 (简化版)

## 🚀 优化实施步骤

### 第一阶段：清理依赖 (Phase 1: Dependency Cleanup)
```bash
# 删除重型AI/ML依赖
- torch==2.2.0
- transformers==4.38.0
- scikit-learn==1.3.2
- nltk==3.8.1
- jieba==0.42.1

# 删除复杂数据处理
- polars==0.19.19
- backtrader==1.9.78.123
- empirical==0.5.5
- pyfolio==0.9.2
- statsmodels==0.14.0
- arch==6.2.0

# 删除新闻处理系统
- newspaper3k==0.2.8
- playwright==1.40.0
- beautifulsoup4==4.12.2
- lxml==4.9.3
- feedparser==6.0.10

# 删除重型数据库
- redis==5.0.1
- hiredis==2.2.3
- celery==5.3.4
- kombu==5.3.4

# 删除可视化库
- plotly==5.17.0
- matplotlib==3.8.2
- seaborn==0.13.0
- mplfinance==0.12.10b0
- wordcloud==1.9.2
```

### 第二阶段：代码重构 (Phase 2: Code Refactoring)
```python
# 简化的项目结构
smart-stock-insider/
├── backend/
│   ├── main.py                 # 主入口 (简化版)
│   ├── api/
│   │   ├── stock.py           # 股票数据API
│   │   └── expert.py          # 专家圆桌API
│   ├── services/
│   │   ├── stock_service.py   # 股票数据服务
│   │   └── glm_service.py     # GLM AI服务
│   └── models/
│       ├── stock.py           # 股票数据模型
│       └── expert.py          # 专家分析模型
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx  # 主仪表板
│   │   │   └── AIAnalysis.tsx # AI分析页面
│   │   ├── components/
│   │   │   └── ExpertRoundTable.tsx # 专家圆桌组件
│   │   └── services/
│   │       └── api.ts         # API客户端
│   └── src-tauri/             # Tauri配置
├── requirements-lite.txt      # 轻量化依赖
└── .env                       # 环境配置
```

### 第三阶段：功能精简 (Phase 3: Feature Simplification)
1. **核心功能保留**
   - 股票基础数据查询
   - GLM-4.5-Flash专家圆桌分析
   - 简洁的桌面界面

2. **移除复杂功能**
   - 复杂的新闻聚合系统
   - 量化回测引擎
   - 高级技术指标计算
   - 多种数据源集成

## 📦 最终依赖清单 (requirements-lite-final.txt)

```txt
# ===== 核心Web框架 =====
fastapi==0.120.2
uvicorn[standard]==0.38.0
python-multipart==0.0.6

# ===== 基础数据处理 =====
akshare==1.17.78
pandas==2.3.3
numpy==2.3.4

# ===== HTTP客户端 =====
httpx==0.27.0
requests==2.31.0

# ===== 数据验证 =====
pydantic==2.8.0
pydantic-settings==2.4.0

# ===== 配置管理 =====
python-dotenv==1.0.0

# ===== 日志 =====
loguru==0.7.2

# ===== 基础存储 =====
aiosqlite==0.20.0

# ===== 工具库 =====
python-dateutil==2.9.0
pytz==2024.1

# 总计: 约15个核心依赖，vs 原来160+个依赖
```

## 🎯 实施优先级

### 🔥 高优先级 (立即执行)
1. 创建新的简化依赖文件
2. 清理backend目录中的复杂模块
3. 保留并优化核心API

### ⚡ 中优先级 (第二步)
1. 重构前端组件，移除复杂功能
2. 优化Tauri配置
3. 集成GLM-4.5-Flash服务

### 📱 低优先级 (最后优化)
1. 界面美化和用户体验优化
2. 添加基础的错误处理
3. 性能优化

## 🚀 预期结果

### ✅ 优化后项目特点
- **轻量化**: 依赖包从160+减少到15个
- **兼容性**: 完美兼容Python 3.12
- **专注性**: 只保留核心AI分析功能
- **稳定性**: 移除复杂依赖，减少故障点
- **维护性**: 代码量减少70%，易于维护

### 🎯 用户价值
- **快速启动**: 无需复杂的依赖安装
- **稳定运行**: 避免依赖冲突
- **专注功能**: 专业的AI投资分析
- **桌面体验**: 原生桌面应用性能

## 📋 执行检查清单

- [ ] 备份现有项目
- [ ] 创建requirements-lite-final.txt
- [ ] 清理backend目录结构
- [ ] 保留核心API文件
- [ ] 测试基础功能
- [ ] 集成GLM专家系统
- [ ] 前端界面简化
- [ ] 端到端测试
- [ ] 性能验证
- [ ] 用户手册更新

---

**总结**: 通过这个删改优化方案，我们将把一个过度复杂的项目转变为一个专注、轻量、稳定的AI投资分析工具，完全符合用户的实际需求。