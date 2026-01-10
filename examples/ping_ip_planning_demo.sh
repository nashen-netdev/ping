#!/bin/bash
# IP 地址规划表 Ping 工具使用示例脚本

# 进入项目目录
cd "$(dirname "$0")/.." || exit

# 激活虚拟环境
source .venv/bin/activate

echo "=========================================="
echo "IP 地址规划表 Ping 工具示例"
echo "=========================================="
echo ""

# 示例 1：基本用法
echo "示例 1：基本用法 - Ping net&sec 所有设备"
echo "------------------------------------------"
echo "命令：ping-ip-planning --file pass/IP地址规划表-金茂.xlsx --sheet \"net&sec\""
echo ""
read -p "按 Enter 继续运行..." 
echo "n" | python3 -m ping_tool.cli_ip_planning --file "pass/IP地址规划表-金茂.xlsx" --sheet "net&sec" --local --max-workers 10 | head -50
echo ""
echo "（输出已截断，完整结果请查看日志文件）"
echo ""

# 示例 2：查看颜色
echo "=========================================="
echo "示例 2：查看表格中使用的颜色"
echo "------------------------------------------"
echo "命令：ping-ip-planning --list-colors"
echo ""
read -p "按 Enter 继续..." 
python3 -m ping_tool.cli_ip_planning --list-colors
echo ""

# 示例 3：只 ping 绿色单元格（如果支持）
echo "=========================================="
echo "示例 3：只 ping 绿色单元格"
echo "------------------------------------------"
echo "命令：ping-ip-planning --color green"
echo ""
read -p "按 Enter 继续..." 
echo "注意：如果 Excel 格式不支持，将自动跳过颜色过滤"
echo "y" | python3 -m ping_tool.cli_ip_planning --color green --local --max-workers 10 | head -30
echo ""
echo "（输出已截断）"
echo ""

# 示例 4：测试其他 sheet
echo "=========================================="
echo "示例 4：测试服务器&安全 sheet"
echo "------------------------------------------"
echo "命令：ping-ip-planning --sheet \"服务器&安全\""
echo ""
read -p "按 Enter 继续（如果 sheet 不存在会报错）..." 
echo "n" | python3 -m ping_tool.cli_ip_planning --sheet "服务器&安全" --local --max-workers 5 2>&1 | head -30
echo ""

echo "=========================================="
echo "演示完成！"
echo "=========================================="
echo ""
echo "提示："
echo "- 完整结果保存在 logs/ 目录"
echo "- 使用 --help 查看所有参数"
echo "- 详细文档：docs/IP_PLANNING_USAGE.md"
echo ""
