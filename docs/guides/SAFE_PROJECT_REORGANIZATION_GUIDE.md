# 基于核心项目计划的安全整理指南

## 🎯 核心指导原则

**重要提醒**: `.claude/plan/ai-enhanced-desktop-app.md` 是当前优化后项目的**核心计划文档**，所有整理工作必须以此文档为准，避免误删重要文件。

## 📋 当前确认的核心技术架构 (基于ai-enhanced-desktop-app.md)

### ✅ 第一阶段: 后端轻量化改造 (已完成)
- **后端**: FastAPI + akshare + GLM-4.5-Flash
- **主入口**: `backend/main_standalone.py`
- **精简依赖**: `requirements-final.txt` (14个核心依赖)
- **GLM集成**: `backend/services/ai_service/glm_analyzer.py`
- **数据服务**: `backend/services/data_service/stock_service_lite.py`
- **专家圆桌**: `backend/services/ai_service/expert_roundtable/round_table_coordinator.py`

### ✅ 第二阶段: AI功能模块开发 (已完成)
- **AI股票分析服务**: GLM-4.5-Flash API集成
- **专家圆桌系统**: 四位AI分析师协作系统
- **真实数据**: akshare API集成

### 🔄 第三阶段: 前端核心组件 (进行中)
- **前端架构**: Tauri 2.0 + React 18 + TypeScript + Antd
- **当前状态**: React + TypeScript + Ant Design (在frontend目录)
- **主要页面**: `frontend/src/pages/AIAnalysis.tsx`
- **AI组件**: `frontend/src/components/AI/ExpertRoundTable.tsx`

### ⏳ 第四、五阶段: 待进行
- AI功能前端集成
- 桌面应用优化 (Tauri)

## 🛡️ 绝对保护的核心文件列表

### 项目计划文档
- `.claude/plan/ai-enhanced-desktop-app.md` - **核心项目计划，绝对不可删除**
- `PROJECT_SUCCESS_REPORT.md` - 项目成功报告
- `ARCHITECTURE.md` - 架构文档

### 后端核心 (Python + FastAPI)
- `backend/main_standalone.py` - 主应用入口
- `backend/requirements-final.txt` - 精简依赖清单
- `backend/services/ai_service/glm_analyzer.py` - GLM-4.5-Flash分析器
- `backend/services/ai_service/expert_roundtable/round_table_coordinator.py` - 专家圆桌协调器
- `backend/services/data_service/stock_service_lite.py` - 股票数据服务

### 前端核心 (React + TypeScript)
- `frontend/package.json` - 前端配置
- `frontend/vite.config.ts` - 构建配置
- `frontend/tsconfig.json` - TypeScript配置
- `frontend/src/pages/AIAnalysis.tsx` - AI分析主页面
- `frontend/src/components/AI/ExpertRoundTable.tsx` - 专家圆桌组件
- `frontend/src/services/api.ts` - API客户端

### 配置文件
- `.env.example` - 环境变量示例
- `README.md` - 项目说明
- `.gitignore` - Git忽略规则

## 📦 可以安全整理的文件

### 🔧 临时工具脚本 (可移动到archived/temp-scripts/)
```
check-tauri-simple.py          # Tauri检查脚本
fix-tauri-setup.py            # Tauri修复脚本
cleanup_project.py            # 清理脚本
cleanup_simple.py             # 简化清理脚本
test_integration.py           # 集成测试脚本
test_integration_simple.py    # 简化测试脚本
quick-start-verify.py         # 快速验证脚本
```

### 📒 过时文档 (可移动到archived/legacy-docs/)
```
PROJECT_STRUCTURE_REVIEW.md   # 已被本指南替代
COMPLETE_SOLUTION_SUMMARY.md  # 旧版总结
docs/ 目录下的过时文档        # 需要逐个检查
```

### 🗑️ 已删除文件的确认 (git status显示D状态)
这些文件已经在git中被标记为删除，整理时可以忽略：
- `go.mod`, `main.go`, `wails.json` - Go相关文件
- `data-service/` - 旧版数据服务
- 大量过时的docs文档
- 构建脚本和配置文件

## 🎯 分阶段安全整理计划

### 第一阶段：创建归档目录结构
```bash
mkdir -p archived/temp-scripts archived/legacy-docs archived/backup-2025-10-29
```

### 第二阶段：移动临时脚本
- 将所有临时Python脚本移动到 `archived/temp-scripts/`
- 保留scripts目录中的有用脚本

### 第三阶段：整理过时文档
- 将确认过时的文档移动到 `archived/legacy-docs/`
- 保留仍有价值的文档

### 第四阶段：验证核心功能
- 测试后端服务启动
- 测试前端界面访问
- 验证GLM-4.5-Flash集成

## ⚠️ 整理执行原则

1. **最小化原则**: 只移动明确不需要的文件
2. **备份原则**: 重要文件先备份再移动
3. **验证原则**: 每次整理后验证核心功能
4. **文档原则**: 及时更新整理记录

## 🚀 整理后的预期项目结构

```
smart-stock-insider/
├── backend/                    # ✅ FastAPI后端
├── frontend/                   # ✅ React前端
├── .claude/plan/              # ✅ 核心项目计划
├── archived/                  # 📦 归档文件
│   ├── temp-scripts/         # 临时脚本
│   ├── legacy-docs/          # 过时文档
│   └── backup-2025-10-29/    # 备份
├── tests/                     # 测试套件
├── scripts/                   # 有用的辅助脚本
├── requirements-final.txt     # ✅ 精简依赖
├── README.md                  # ✅ 项目说明
└── ARCHITECTURE.md            # ✅ 架构文档
```

## 📊 成功标准

**核心功能保持完整**:
- ✅ GLM-4.5-Flash专家圆桌系统正常运行
- ✅ FastAPI后端服务正常启动 (http://localhost:8001)
- ✅ React前端界面正常访问 (http://localhost:10001)
- ✅ akshare股票数据服务正常
- ✅ API文档正常访问 (http://localhost:8001/docs)

**项目结构优化**:
- 🗂️ 文件分类清晰，易于查找
- 📦 项目体积减少
- 🧹 代码库整洁，维护性提升
- 📋 文档结构合理

---

## ⚠️ 执行提醒

**必须遵守的规则**:
1. 任何文件移动前，必须对照ai-enhanced-desktop-app.md确认
2. 不确定用途的文件，保留在原位置
3. 每个操作步骤后都要验证系统功能
4. 遇到疑问立即停止，寻求确认

**核心原则**: 宁可保守，不可误删。确保AI增强轻量化专业版的完整功能。

---

*本指南基于用户反馈和核心项目计划文档制定，确保整理工作的安全性和准确性。*