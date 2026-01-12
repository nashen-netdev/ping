.PHONY: help install install-dev test lint format clean clean-logs clean-all run run-ip-planning demo-ip-planning

# 默认目标
help:
	@echo "Ping Tool - Makefile 命令:"
	@echo ""
	@echo "  make install       - 安装项目依赖"
	@echo "  make install-dev   - 安装开发依赖"
	@echo "  make test          - 运行测试"
	@echo "  make lint          - 运行代码检查"
	@echo "  make format        - 格式化代码"
	@echo "  make clean         - 清理临时文件（Python缓存、编译文件等）"
	@echo "  make clean-logs    - 清理旧日志文件（7天前）"
	@echo "  make clean-all     - 深度清理（临时文件 + 日志 + 系统文件）"
	@echo "  make run           - 运行程序"
	@echo "  make run-ip-planning - 运行 IP 规划表 Ping 工具"
	@echo "  make demo-ip-planning - 运行 IP 规划表演示脚本"
	@echo "  make build         - 构建包"
	@echo "  make docs          - 生成文档"
	@echo ""

# 安装依赖
install:
	python3 -m pip install -e .

# 安装开发依赖
install-dev:
	python3 -m pip install -e ".[dev]"

# 运行测试
test:
	python3 -m pytest tests/ -v --cov=src/ping_tool --cov-report=html

# 代码检查
lint:
	python3 -m flake8 src/ping_tool tests/
	python3 -m mypy src/ping_tool

# 格式化代码
format:
	python3 -m black src/ping_tool tests/
	python3 -m isort src/ping_tool tests/

# 清理临时文件
clean:
	@echo "清理 Python 临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*.swp" -delete
	find . -type f -name "*.bak" -delete
	find . -type f -name "*.tmp" -delete
	rm -rf build/ dist/
	@echo "✓ 清理完成"

# 清理旧日志文件
clean-logs:
	@echo "清理 7 天前的日志文件..."
	@find logs/ -name "*.log" -type f -mtime +7 -exec echo "  删除: {}" \; -delete 2>/dev/null || true
	@echo "✓ 日志清理完成"

# 深度清理（所有临时文件 + 日志）
clean-all: clean clean-logs
	@echo "✓ 深度清理完成！"

# 运行程序
run:
	python3 -m ping_tool

# 运行 IP 规划表 Ping 工具
run-ip-planning:
	python3 -m ping_tool.cli_ip_planning --file pass/IP地址规划表-金茂1.xlsx --sheet "net&sec"

# 运行 IP 规划表演示脚本
demo-ip-planning:
	@bash examples/ping_ip_planning_demo.sh

# 构建包
build:
	python3 -m pip install --upgrade build
	python3 -m build

# 生成文档
docs:
	@echo "文档位于 README.md 和 docs/ 目录"

