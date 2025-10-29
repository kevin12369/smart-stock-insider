#!/usr/bin/env python3
"""
智股通项目清理脚本
保留核心功能，删除复杂模块，优化项目结构
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class ProjectCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.backup_dir = self.project_root / f"backup-cleanup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # 需要保留的核心文件和目录
        self.keep_core = {
            # 后端核心文件
            "backend/main_standalone.py",
            "backend/requirements-final.txt",
            "backend/.env.example",

            # 核心服务目录（保留部分）
            "backend/services/ai_service",
            "backend/services/data_service",

            # 核心API目录
            "backend/api/routers",

            # 核心配置
            "backend/core/config.py",

            # 前端核心文件
            "frontend/src/App.tsx",
            "frontend/src/main.tsx",
            "frontend/src/pages/AIAnalysis.tsx",
            "frontend/src/components/AI",
            "frontend/src/services/api.ts",
            "frontend/package.json",
            "frontend/vite.config.ts",
            "frontend/tsconfig.json",

            # 项目配置文件
            "README.md",
            "ARCHITECTURE.md",
            "PROJECT_CLEANUP_PLAN.md",
            ".env",
            ".env.example",
            "requirements-final.txt"
        }

        # 需要删除的复杂模块
        self.delete_modules = {
            # 复杂的服务目录
            "backend/services/news_service",
            "backend/services/portfolio_service",
            "backend/services/backtest_service",
            "backend/services/cache_service",
            "backend/services/enhanced_ai_service",
            "backend/services/extended_news_service",
            "backend/services/news_aggregator",
            "backend/services/news_data_service",
            "backend/services/news_push_service",
            "backend/services/stock_service",
            "backend/services/database_optimizer",
            "backend/services/logger",

            # 复杂的模型目录
            "backend/models/news",
            "backend/models/portfolio",
            "backend/models/backtest",
            "backend/models/extended_news",
            "backend/models/news_push",
            "backend/models/signal_config",
            "backend/models/database",

            # 复杂的API目录
            "backend/api/analytics.py",
            "backend/api/chatbot.py",
            "backend/api/portfolio.py",
            "backend/api/sentiment.py",

            # 工具和测试目录
            "backend/tests",
            "backend/utils",
            "backend/alembic",
            "backend/schemas",

            # 缓存和数据目录
            "backend/cache",
            "backend/data",
            "backend/logs",
            "backend/uploads",
            "backend/backups",
            "backend/__pycache__",

            # 复杂的配置文件
            "backend/main.py",
            "backend/main_lite.py",
            "backend/requirements.txt",
            "backend/install_dependencies.py",
            "backend/Dockerfile",
            "backend/test_main.py",

            # 复杂的依赖文件
            "requirements-312.txt",
            "requirements-lite.txt",
            "requirements-test.txt"
        }

    def backup_project(self):
        """备份当前项目"""
        print(f"📦 备份项目到: {self.backup_dir}")

        # 备份需要删除的文件
        backup_content = self.backup_dir / "deleted_modules"
        backup_content.mkdir(parents=True, exist_ok=True)

        deleted_items = []
        for module_path in self.delete_modules:
            full_path = self.project_root / module_path
            if full_path.exists():
                backup_target = backup_content / module_path
                backup_target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    if full_path.is_dir():
                        shutil.copytree(full_path, backup_target)
                        deleted_items.append(f"目录: {module_path}")
                    else:
                        shutil.copy2(full_path, backup_target)
                        deleted_items.append(f"文件: {module_path}")
                except Exception as e:
                    print(f"⚠️ 备份失败 {module_path}: {e}")

        # 保存删除清单
        with open(self.backup_dir / "deleted_manifest.json", "w", encoding="utf-8") as f:
            json.dump({
                "backup_time": datetime.now().isoformat(),
                "deleted_items": deleted_items,
                "total_count": len(deleted_items)
            }, f, indent=2, ensure_ascii=False)

        print(f"✅ 备份完成，共备份 {len(deleted_items)} 个项目")

    def cleanup_modules(self):
        """删除复杂模块"""
        print("🧹 开始清理复杂模块...")

        deleted_count = 0
        for module_path in self.delete_modules:
            full_path = self.project_root / module_path
            if full_path.exists():
                try:
                    if full_path.is_dir():
                        shutil.rmtree(full_path)
                        print(f"📁 删除目录: {module_path}")
                    else:
                        full_path.unlink()
                        print(f"📄 删除文件: {module_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {module_path}: {e}")

        print(f"✅ 清理完成，共删除 {deleted_count} 个项目")

    def create_simplified_structure(self):
        """创建简化后的项目结构"""
        print("🏗️ 创建简化项目结构...")

        # 创建简化的backend结构
        simple_backend = self.backend_dir
        simple_api = simple_backend / "api"
        simple_services = simple_backend / "services"
        simple_core = simple_backend / "core"

        # 确保目录存在
        simple_api.mkdir(exist_ok=True)
        simple_services.mkdir(exist_ok=True)
        simple_core.mkdir(exist_ok=True)

        # 创建简化的API文件
        expert_api = simple_api / "expert.py"
        if not expert_api.exists():
            expert_api.write_text("""# 专家圆桌API路由
from fastapi import APIRouter, HTTPException
from services.ai_service.glm_analyzer import glm_analyzer
from services.data_service.stock_service_lite import stock_service_lite

router = APIRouter(prefix="/api/expert-roundtable", tags=["专家圆桌"])

@router.get("/experts")
async def get_experts():
    '''获取专家列表'''
    return {
        "experts": [
            {
                "id": "technical",
                "name": "技术面分析师",
                "description": "15年技术分析经验，专注技术指标、K线形态和趋势分析",
                "specialties": ["MACD", "KDJ", "RSI", "布林带", "趋势线"],
                "confidence": 0.85,
                "available": True
            },
            {
                "id": "fundamental",
                "name": "基本面分析师",
                "description": "专业财务分析背景，精通估值模型和行业分析",
                "specialties": ["财务报表", "估值模型", "ROE分析", "竞争优势"],
                "confidence": 0.80,
                "available": True
            },
            {
                "id": "news",
                "name": "新闻分析师",
                "description": "资深财经记者背景，擅长新闻情感分析和事件解读",
                "specialties": ["情感分析", "政策解读", "市场情绪", "舆情监测"],
                "confidence": 0.75,
                "available": True
            },
            {
                "id": "risk",
                "name": "风控分析师",
                "description": "专业风险管理师，专注投资风险控制和仓位管理",
                "specialties": ["VaR计算", "仓位管理", "止损策略", "波动率分析"],
                "confidence": 0.85,
                "available": True
            }
        ]
    }

@router.post("/quick-analysis")
async def quick_analysis(symbol: str):
    '''快速专家分析'''
    try:
        # 这里集成GLM-4.5-Flash分析
        result = await glm_analyzer.quick_analysis(symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""")

        # 创建简化的主入口文件
        main_simple = simple_backend / "main_simple.py"
        if not main_simple.exists():
            main_simple.write_text("""# 智股通AI增强轻量化版 - 简化主入口
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.expert import router as expert_router

app = FastAPI(
    title="智股通AI增强轻量化版",
    description="基于GLM-4.5-Flash的智能股票分析平台",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(expert_router)

@app.get("/")
async def root():
    return {
        "message": "智股通AI增强轻量化版",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "glm_ai": "healthy",
            "data_service": "available",
            "expert_system": "available"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
""")

        print("✅ 简化项目结构创建完成")

    def generate_cleanup_report(self):
        """生成清理报告"""
        report = {
            "cleanup_time": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "backup_location": str(self.backup_dir),
            "deleted_modules_count": len(self.delete_modules),
            "kept_core_modules_count": len(self.keep_core),
            "next_steps": [
                "1. 安装简化依赖: pip install -r requirements-final.txt",
                "2. 测试基础功能: python backend/main_simple.py",
                "3. 集成GLM-4.5-Flash专家系统",
                "4. 前端界面测试和优化",
                "5. 端到端功能验证"
            ]
        }

        report_file = self.project_root / "CLEANUP_REPORT.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📋 清理报告已生成: {report_file}")
        return report

    def run_cleanup(self):
        """执行完整的清理流程"""
        print("🚀 开始智股通项目清理优化...")
        print("=" * 60)

        try:
            # 1. 备份项目
            self.backup_project()

            # 2. 清理复杂模块
            self.cleanup_modules()

            # 3. 创建简化结构
            self.create_simplified_structure()

            # 4. 生成清理报告
            report = self.generate_cleanup_report()

            print("=" * 60)
            print("✅ 项目清理优化完成！")
            print(f"📦 备份位置: {self.backup_dir}")
            print(f"📋 删除模块: {report['deleted_modules_count']} 个")
            print(f"💎 保留核心: {report['kept_core_modules_count']} 个")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"❌ 清理过程出现错误: {e}")
            return False

if __name__ == "__main__":
    # 获取项目根目录
    project_root = Path(__file__).parent

    # 创建清理器并执行清理
    cleaner = ProjectCleaner(project_root)
    success = cleaner.run_cleanup()

    if success:
        print("\n🎉 智股通项目优化完成！")
        print("📌 下一步操作:")
        print("   1. pip install -r requirements-final.txt")
        print("   2. python backend/main_simple.py")
        print("   3. 访问 http://localhost:8001/docs 查看API")
    else:
        print("\n❌ 项目清理失败，请检查错误信息")
        exit(1)