# 智能投研项目 Makefile
# 提供常用的开发和测试命令

.PHONY: help install install-dev test test-unit test-integration test-e2e test-ai test-api test-performance test-all test-slow
.PHONY: lint format type-check security clean coverage report quality setup-dev

# 默认目标
help:
	@echo "智能投研项目 - 可用命令:"
	@echo ""
	@echo "安装和设置:"
	@echo "  install        安装生产依赖"
	@echo "  install-dev    安装开发依赖"
	@echo "  setup-dev      设置开发环境"
	@echo ""
	@echo "测试:"
	@echo "  test           运行所有测试"
	@echo "  test-unit      运行单元测试"
	@echo "  test-integration 运行集成测试"
	@echo "  test-e2e       运行端到端测试"
	@echo "  test-ai        运行AI功能测试"
	@echo "  test-api       运行API接口测试"
	@echo "  test-performance 运行性能测试"
	@echo "  test-slow      运行慢速测试"
	@echo "  test-all       运行所有测试（包括慢速）"
	@echo ""
	@echo "代码质量:"
	@echo "  lint           运行代码风格检查"
	@echo "  format         格式化代码"
	@echo "  type-check     运行类型检查"
	@echo "  security       运行安全检查"
	@echo "  quality        运行所有质量检查"
	@echo ""
	@echo "报告和清理:"
	@echo "  coverage       生成覆盖率报告"
	@echo "  report         生成完整测试报告"
	@echo "  clean          清理测试产物"
	@echo ""
	@echo "开发:"
	@echo "  dev            启动开发服务器"
	@echo "  build          构建项目"
	@echo "  docker-build   构建Docker镜像"

# 安装依赖
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

setup-dev: install-dev
	@echo "设置开发环境完成"
	@echo "请确保已安装Redis和数据库服务"

# 测试命令
test:
	python scripts/run_tests.py all

test-unit:
	python scripts/run_tests.py unit

test-integration:
	python scripts/run_tests.py integration

test-e2e:
	python scripts/run_tests.py e2e

test-ai:
	python scripts/run_tests.py ai

test-api:
	python scripts/run_tests.py api

test-performance:
	python scripts/run_tests.py performance

test-slow:
	python scripts/run_tests.py slow

test-all:
	python scripts/run_tests.py all --coverage --report

# 代码质量检查
lint:
	flake8 backend/ tests/
	@echo "代码风格检查完成"

format:
	black backend/ tests/
	isort backend/ tests/
	@echo "代码格式化完成"

type-check:
	mypy backend/
	@echo "类型检查完成"

security:
	bandit -r backend/
	@echo "安全检查完成"

quality: lint type-check security
	@echo "所有质量检查完成"

# 覆盖率和报告
coverage:
	python scripts/run_tests.py all --coverage
	@echo "覆盖率报告已生成到 htmlcov/ 目录"

report:
	python scripts/run_tests.py all --coverage --report
	@echo "测试报告已生成"

# 清理
clean:
	python scripts/run_tests.py --cleanup
	rm -rf .pytest_cache .coverage htmlcov/ *.xml
	rm -rf **/__pycache__ **/*.pyc **/*.pyo
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "清理完成"

# 开发服务器
dev:
	@echo "启动后端开发服务器..."
	cd backend && python main.py

# 构建
build:
	@echo "构建前端..."
	cd frontend && npm run build
	@echo "前端构建完成"

# Docker
docker-build:
	docker build -t smart-stock-insider .
	@echo "Docker镜像构建完成"

# 快速测试命令（用于开发）
test-quick:
	pytest tests/unit -x -v --tb=short

test-watch:
	pytest-watch tests/unit

# 数据库操作
db-setup:
	@echo "设置测试数据库..."
	# 这里可以添加数据库设置命令

db-reset:
	@echo "重置测试数据库..."
	# 这里可以添加数据库重置命令

# 文档生成
docs:
	@echo "生成API文档..."
	# 这里可以添加文档生成命令

# 预提交检查
pre-commit: format lint test-unit
	@echo "预提交检查完成"

# CI/CD相关
ci-test:
	python scripts/run_tests.py all --coverage --quality

ci-build:
	$(MAKE) clean
	$(MAKE) ci-test
	$(MAKE) build

# 性能基准
benchmark:
	python scripts/run_tests.py performance
	@echo "性能基准测试完成"

# 内存检查
memory-check:
	mprof run python scripts/run_tests.py unit
	@echo "内存使用分析完成"

# 依赖安全检查
deps-check:
	safety check
	pip-audit
	@echo "依赖安全检查完成"

# 发布相关
version:
	@python -c "import backend.version; print(backend.version.VERSION)"

tag:
	@echo "创建Git标签..."
	git tag -a v$(shell make version) -m "Release version $(shell make version)"
	git push origin v$(shell make version)

# 开发工具检查
check-tools:
	@echo "检查开发工具..."
	@python --version
	@pip --version
	@node --version || echo "Node.js 未安装"
	@npm --version || echo "npm 未安装"
	@docker --version || echo "Docker 未安装"
	@redis-server --version || echo "Redis 未安装"
	@echo "开发工具检查完成"