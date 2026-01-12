#!/bin/bash
# 日志清理脚本
# 清理指定天数前的日志文件

set -e

# 默认清理 7 天前的日志
DAYS=${1:-7}

# 脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="${PROJECT_ROOT}/logs"

echo "================================================"
echo "日志清理脚本"
echo "================================================"
echo "项目目录: ${PROJECT_ROOT}"
echo "日志目录: ${LOGS_DIR}"
echo "清理策略: 删除 ${DAYS} 天前的日志文件"
echo "================================================"
echo ""

# 检查日志目录是否存在
if [ ! -d "${LOGS_DIR}" ]; then
    echo "✗ 日志目录不存在: ${LOGS_DIR}"
    exit 1
fi

# 统计日志文件
TOTAL_LOGS=$(find "${LOGS_DIR}" -name "*.log" -type f 2>/dev/null | wc -l | tr -d ' ')
OLD_LOGS=$(find "${LOGS_DIR}" -name "*.log" -type f -mtime +${DAYS} 2>/dev/null | wc -l | tr -d ' ')

echo "当前日志文件数量: ${TOTAL_LOGS}"
echo "需要清理的日志数量: ${OLD_LOGS}"
echo ""

if [ "${OLD_LOGS}" -eq 0 ]; then
    echo "✓ 没有需要清理的日志文件"
    exit 0
fi

# 显示要删除的文件
echo "将要删除以下日志文件:"
echo "----------------------------------------"
find "${LOGS_DIR}" -name "*.log" -type f -mtime +${DAYS} -exec ls -lh {} \; 2>/dev/null | awk '{print "  "$9" ("$5")"}'
echo "----------------------------------------"
echo ""

# 询问确认
read -p "确认删除这些文件？(y/n) [n]: " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "✗ 已取消清理"
    exit 0
fi

# 执行删除
echo ""
echo "正在删除旧日志..."
find "${LOGS_DIR}" -name "*.log" -type f -mtime +${DAYS} -exec rm -f {} \;

# 统计剩余日志
REMAINING_LOGS=$(find "${LOGS_DIR}" -name "*.log" -type f 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "✓ 清理完成！"
echo "  已删除: ${OLD_LOGS} 个文件"
echo "  剩余: ${REMAINING_LOGS} 个文件"
echo ""
