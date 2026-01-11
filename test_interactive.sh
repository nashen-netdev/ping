#!/bin/bash
# 测试交互式输入

cd /Users/sen/automate/Network_Projects/ethernet/ping
source .venv/bin/activate

# 模拟输入：回车（进入手动模式）-> 文件路径 -> 选择1 -> 选择n（不过滤）-> 确认y
echo -e "\n/Users/sen/Desktop/IP地址规划表-金茂1.xlsx\n1\nn\ny" | ping-ip-planning
