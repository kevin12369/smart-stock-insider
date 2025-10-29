#!/usr/bin/env python3
"""
智股通项目简化清理脚本
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

def main():
    """执行项目清理"""
    project_root = Path(".")
    backend_dir = project_root / "backend"

    print("=" * 60)
    print("智股通项目清理优化")
    print("=" * 60)
    print(f"项目路径: {project_root.absolute()}")

    # 创建备份目录
    backup_dir = project_root / f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    backup_dir.mkdir(exist_ok=True)
    print(f"备份目录: {backup_dir}")

    # 需要删除的复杂模块列表
    modules_to_delete = [
        "backend/alembic",
        "backend/api/analytics.py",
        "backend/api/chatbot.py",
        "backend/api/portfolio.py",
        "backend/api/sentiment.py",
        "backend/cache",
        "backend/data",
        "backend/logs",
        "backend/uploads",
        "backend/backups",
        "backend/__pycache__",
        "backend/tests",
        "backend/utils",
        "backend/schemas",
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
        "backend/models/news",
        "backend/models/portfolio",
        "backend/models/backtest",
        "backend/models/extended_news",
        "backend/models/news_push",
        "backend/models/signal_config",
        "backend/models/database",
        "backend/main.py",
        "backend/main_lite.py",
        "backend/requirements.txt",
        "backend/install_dependencies.py",
        "backend/Dockerfile",
        "backend/test_main.py",
        "requirements-312.txt",
        "requirements-lite.txt",
        "requirements-test.txt"
    ]

    deleted_count = 0
    backup_count = 0

    # 1. 备份并删除模块
    print("\n开始备份和删除复杂模块...")
    for module_path in modules_to_delete:
        full_path = project_root / module_path
        if full_path.exists():
            # 备份
            backup_target = backup_dir / module_path
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            try:
                if full_path.is_dir():
                    shutil.copytree(full_path, backup_target)
                    shutil.rmtree(full_path)
                    print(f"✓ 备份并删除目录: {module_path}")
                else:
                    backup_target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(full_path, backup_target)
                    full_path.unlink()
                    print(f"✓ 备份并删除文件: {module_path}")
                deleted_count += 1
                backup_count += 1
            except Exception as e:
                print(f"✗ 处理失败 {module_path}: {e}")

    # 2. 创建简化结构
    print("\n创建简化项目结构...")

    # 确保核心目录存在
    (backend_dir / "api").mkdir(exist_ok=True)
    (backend_dir / "services").mkdir(exist_ok=True)
    (backend_dir / "core").mkdir(exist_ok=True)

    # 3. 生成清理报告
    report = {
        "cleanup_time": datetime.now().isoformat(),
        "backup_dir": str(backup_dir),
        "deleted_count": deleted_count,
        "backup_count": backup_count
    }

    with open(project_root / "cleanup_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n清理完成!")
    print(f"- 删除模块: {deleted_count} 个")
    print(f"- 备份位置: {backup_dir}")
    print(f"- 清理报告: cleanup_report.json")

    print("\n下一步操作:")
    print("1. pip install -r requirements-final.txt")
    print("2. python backend/main_standalone.py")
    print("3. 测试基础功能")

    return True

if __name__ == "__main__":
    try:
        main()
        print("\n项目清理优化完成!")
    except Exception as e:
        print(f"\n清理失败: {e}")
        exit(1)