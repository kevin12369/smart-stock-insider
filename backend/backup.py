"""
数据备份模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import os
import shutil
import sqlite3
import logging
import asyncio
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from zipfile import ZipFile, ZIP_DEFLATED

from core.config import settings
from core.cache import cache_manager

logger = logging.getLogger(__name__)


class BackupManager:
    """备份管理器"""

    def __init__(self):
        self.backup_dir = Path(settings.BACKUP_PATH)
        self.backup_interval = timedelta(hours=settings.BACKUP_INTERVAL)
        self.max_backups = 30  # 最多保留30个备份
        self.compression_enabled = True

    async def initialize(self):
        """初始化备份管理器"""
        try:
            # 确保备份目录存在
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # 创建子目录
            (self.backup_dir / "database").mkdir(exist_ok=True)
            (self.backup_dir / "config").mkdir(exist_ok=True)
            (self.backup_dir / "logs").mkdir(exist_ok=True)

            logger.info(f"✅ 备份管理器初始化成功，备份目录: {self.backup_dir}")

        except Exception as e:
            logger.error(f"❌ 备份管理器初始化失败: {e}")
            raise

    async def create_full_backup(self, description: Optional[str] = None) -> Dict[str, Any]:
        """
        创建完整备份

        Args:
            description: 备份描述

        Returns:
            备份信息字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        try:
            backup_path.mkdir(exist_ok=True)

            # 备份数据库
            db_result = await self._backup_database(backup_path)

            # 备份配置文件
            config_result = await self._backup_config(backup_path)

            # 备份日志文件
            logs_result = await self._backup_logs(backup_path)

            # 备份缓存数据（可选）
            cache_result = await self._backup_cache(backup_path)

            # 创建备份元数据
            metadata = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "description": description or f"自动备份 - {timestamp}",
                "components": {
                    "database": db_result,
                    "config": config_result,
                    "logs": logs_result,
                    "cache": cache_result
                },
                "total_size": self._calculate_backup_size(backup_path),
                "created_at": datetime.now().isoformat()
            }

            # 保存元数据
            metadata_path = backup_path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # 压缩备份
            if self.compression_enabled:
                await self._compress_backup(backup_path)

            # 清理旧备份
            await self._cleanup_old_backups()

            logger.info(f"✅ 完整备份创建成功: {backup_name}")
            return metadata

        except Exception as e:
            logger.error(f"❌ 创建完整备份失败: {e}")
            # 清理失败的备份
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise

    async def _backup_database(self, backup_path: Path) -> Dict[str, Any]:
        """备份数据库"""
        try:
            db_backup_dir = backup_path / "database"
            db_backup_dir.mkdir(exist_ok=True)

            # 备份SQLite数据库
            db_source = Path("data/smart_stock.db")
            if db_source.exists():
                db_target = db_backup_dir / "smart_stock.db"
                shutil.copy2(db_source, db_target)

                # 验证备份
                if self._verify_sqlite_backup(db_target):
                    size = db_target.stat().st_size
                    logger.info(f"✅ 数据库备份成功: {size} bytes")
                    return {
                        "status": "success",
                        "size": size,
                        "path": str(db_target.relative_to(backup_path)),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise Exception("数据库备份验证失败")
            else:
                raise Exception("源数据库文件不存在")

        except Exception as e:
            logger.error(f"❌ 数据库备份失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _backup_config(self, backup_path: Path) -> Dict[str, Any]:
        """备份配置文件"""
        try:
            config_backup_dir = backup_path / "config"
            config_backup_dir.mkdir(exist_ok=True)

            backed_up_files = []
            total_size = 0

            # 需要备份的配置文件
            config_files = [
                ".env",
                "config.json",
                "alembic.ini",
                "backend/alembic.ini"
            ]

            for config_file in config_files:
                source_path = Path(config_file)
                if source_path.exists():
                    target_path = config_backup_dir / config_file
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)

                    size = target_path.stat().st_size
                    backed_up_files.append({
                        "file": config_file,
                        "size": size,
                        "path": str(target_path.relative_to(backup_path))
                    })
                    total_size += size

            logger.info(f"✅ 配置文件备份成功: {len(backed_up_files)} 个文件, {total_size} bytes")
            return {
                "status": "success",
                "files": backed_up_files,
                "total_size": total_size,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 配置文件备份失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _backup_logs(self, backup_path: Path) -> Dict[str, Any]:
        """备份日志文件"""
        try:
            logs_backup_dir = backup_path / "logs"
            logs_backup_dir.mkdir(exist_ok=True)

            backed_up_files = []
            total_size = 0

            # 需要备份的日志目录
            log_dirs = [
                "logs",
                "backend/logs"
            ]

            for log_dir in log_dirs:
                source_dir = Path(log_dir)
                if source_dir.exists() and source_dir.is_dir():
                    target_dir = logs_backup_dir / log_dir.replace("/", "_")
                    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)

                    # 计算大小
                    for root, dirs, files in os.walk(target_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)

                    backed_up_files.append({
                        "directory": log_dir,
                        "target": str(target_dir.relative_to(backup_path))
                    })

            logger.info(f"✅ 日志文件备份成功: {len(backed_up_files)} 个目录, {total_size} bytes")
            return {
                "status": "success",
                "directories": backed_up_files,
                "total_size": total_size,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 日志文件备份失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _backup_cache(self, backup_path: Path) -> Dict[str, Any]:
        """备份缓存数据"""
        try:
            cache_backup_dir = backup_path / "cache"
            cache_backup_dir.mkdir(exist_ok=True)

            # 导出Redis数据
            if cache_manager.redis_client:
                cache_file = cache_backup_dir / "redis_dump.rdb"
                # 这里简化处理，实际项目中可能需要使用Redis的BGSAVE命令
                # 或者使用Redis的DUMP/RESTORE命令来备份特定键

                # 获取缓存统计信息
                stats = await cache_manager.get_stats()
                stats_file = cache_backup_dir / "cache_stats.json"
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)

                logger.info("✅ 缓存统计信息备份成功")
                return {
                    "status": "success",
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning("⚠️ Redis未连接，跳过缓存备份")
                return {
                    "status": "skipped",
                    "reason": "Redis未连接",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"❌ 缓存备份失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _verify_sqlite_backup(self, backup_path: Path) -> bool:
        """验证SQLite备份"""
        try:
            with sqlite3.connect(str(backup_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                return result[0] == "ok"
        except Exception as e:
            logger.error(f"SQLite备份验证失败: {e}")
            return False

    def _calculate_backup_size(self, backup_path: Path) -> int:
        """计算备份大小"""
        total_size = 0
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        return total_size

    async def _compress_backup(self, backup_path: Path):
        """压缩备份"""
        try:
            zip_path = backup_path.with_suffix('.zip')

            with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_path)
                        zipf.write(file_path, arcname)

            # 删除未压缩的备份目录
            shutil.rmtree(backup_path)

            logger.info(f"✅ 备份压缩成功: {zip_path.name}")

        except Exception as e:
            logger.error(f"❌ 备份压缩失败: {e}")

    async def _cleanup_old_backups(self):
        """清理旧备份"""
        try:
            backups = []
            for item in self.backup_dir.iterdir():
                if item.is_dir() and item.name.startswith('backup_'):
                    backups.append(item)
                elif item.is_file() and item.name.startswith('backup_') and item.suffix == '.zip':
                    backups.append(item)

            # 按修改时间排序
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 保留最新的N个备份
            if len(backups) > self.max_backups:
                for old_backup in backups[self.max_backups:]:
                    if old_backup.is_dir():
                        shutil.rmtree(old_backup)
                    else:
                        old_backup.unlink()
                    logger.info(f"🗑️ 删除旧备份: {old_backup.name}")

        except Exception as e:
            logger.error(f"❌ 清理旧备份失败: {e}")

    async def restore_backup(self, backup_name: str, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        恢复备份

        Args:
            backup_name: 备份名称
            components: 要恢复的组件列表，None表示全部

        Returns:
            恢复结果
        """
        try:
            # 查找备份文件
            backup_path = self._find_backup(backup_name)
            if not backup_path:
                raise Exception(f"备份不存在: {backup_name}")

            # 读取元数据
            metadata = self._load_backup_metadata(backup_path)

            # 恢复组件
            restore_results = {}
            if components is None:
                components = list(metadata["components"].keys())

            for component in components:
                if component in metadata["components"]:
                    result = await self._restore_component(backup_path, component)
                    restore_results[component] = result
                else:
                    restore_results[component] = {
                        "status": "failed",
                        "error": "组件不存在于备份中"
                    }

            logger.info(f"✅ 备份恢复完成: {backup_name}")
            return {
                "backup_name": backup_name,
                "restored_components": restore_results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 备份恢复失败: {e}")
            raise

    def _find_backup(self, backup_name: str) -> Optional[Path]:
        """查找备份文件"""
        # 首先查找压缩文件
        zip_path = self.backup_dir / f"{backup_name}.zip"
        if zip_path.exists():
            return zip_path

        # 然后查找目录
        dir_path = self.backup_dir / backup_name
        if dir_path.exists() and dir_path.is_dir():
            return dir_path

        return None

    def _load_backup_metadata(self, backup_path: Path) -> Dict[str, Any]:
        """加载备份元数据"""
        if backup_path.suffix == '.zip':
            # 从ZIP文件中读取元数据
            with ZipFile(backup_path, 'r') as zipf:
                with zipf.open('metadata.json') as f:
                    return json.load(f)
        else:
            # 从目录中读取元数据
            metadata_path = backup_path / "metadata.json"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)

    async def _restore_component(self, backup_path: Path, component: str) -> Dict[str, Any]:
        """恢复特定组件"""
        try:
            if backup_path.suffix == '.zip':
                # 从ZIP文件恢复
                with ZipFile(backup_path, 'r') as zipf:
                    # 这里需要实现从ZIP恢复的逻辑
                    pass
            else:
                # 从目录恢复
                component_dir = backup_path / component

                if component == "database":
                    return await self._restore_database(component_dir)
                elif component == "config":
                    return await self._restore_config(component_dir)
                elif component == "logs":
                    return await self._restore_logs(component_dir)
                elif component == "cache":
                    return await self._restore_cache(component_dir)

        except Exception as e:
            logger.error(f"❌ 恢复组件 {component} 失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _restore_database(self, backup_dir: Path) -> Dict[str, Any]:
        """恢复数据库"""
        try:
            source_db = backup_dir / "smart_stock.db"
            target_db = Path("data/smart_stock.db")

            if source_db.exists():
                # 创建目标目录
                target_db.parent.mkdir(parents=True, exist_ok=True)

                # 备份当前数据库
                if target_db.exists():
                    backup_current = target_db.with_suffix('.db.backup')
                    shutil.copy2(target_db, backup_current)

                # 恢复数据库
                shutil.copy2(source_db, target_db)

                # 验证恢复
                if self._verify_sqlite_backup(target_db):
                    logger.info("✅ 数据库恢复成功")
                    return {"status": "success"}
                else:
                    raise Exception("数据库恢复验证失败")
            else:
                raise Exception("备份数据库文件不存在")

        except Exception as e:
            logger.error(f"❌ 数据库恢复失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def get_backup_list(self) -> List[Dict[str, Any]]:
        """获取备份列表"""
        backups = []

        for item in self.backup_dir.iterdir():
            if item.name.startswith('backup_'):
                try:
                    if item.suffix == '.zip':
                        metadata = self._load_backup_metadata(item)
                    elif item.is_dir():
                        metadata = self._load_backup_metadata(item)
                    else:
                        continue

                    backups.append({
                        "name": metadata["backup_name"],
                        "timestamp": metadata["timestamp"],
                        "description": metadata.get("description", ""),
                        "size": metadata.get("total_size", 0),
                        "components": list(metadata["components"].keys()),
                        "created_at": metadata["created_at"]
                    })

                except Exception as e:
                    logger.warning(f"⚠️ 读取备份元数据失败 {item.name}: {e}")

        # 按时间排序
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups

    async def schedule_backup(self):
        """调度定期备份"""
        while True:
            try:
                await asyncio.sleep(self.backup_interval.total_seconds())

                if settings.BACKUP_ENABLED:
                    logger.info("🔄 开始定期备份")
                    await self.create_full_backup("定期自动备份")
                else:
                    logger.debug("⏸️ 备份功能已禁用，跳过定期备份")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 定期备份失败: {e}")
                await asyncio.sleep(300)  # 失败后等待5分钟再重试


# 全局备份管理器实例
backup_manager = BackupManager()