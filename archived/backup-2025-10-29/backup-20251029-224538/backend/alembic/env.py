"""
Alembic环境配置

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.database import Base
from core.config import settings
from models import *  # 导入所有模型

# 获取Alembic配置对象
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解释配置文件的日志记录
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 为'autogenerate'支持添加模型的MetaData对象
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。

    这将上下文配置为只需一个URL
    而不是Engine，尽管Engine也是可以接受的
    在这里。通过跳过Engine创建，我们甚至不需要
    有DBAPI可用来使用。

    调用此上下文不会发出连接到数据库的请求。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移。

    在这种情况下，我们需要创建一个Engine
    并将连接与该上下文关联。

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()