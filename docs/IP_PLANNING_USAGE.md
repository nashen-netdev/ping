# IP 地址规划表 Ping 工具使用指南

## 快速开始

### 1. 基本使用

```bash
# 激活虚拟环境
cd /Users/sen/automate/Network_Projects/ethernet/ping
source .venv/bin/activate

# 基本用法：ping net&sec sheet 的所有设备
ping-ip-planning --file pass/IP地址规划表-金茂.xlsx --sheet "net&sec"

# 或使用 Python 模块方式
python3 -m ping_tool.cli_ip_planning --file pass/IP地址规划表-金茂.xlsx --sheet "net&sec"
```

### 2. 交互式使用

运行时会询问是否只 ping 绿色单元格：

```bash
$ ping-ip-planning --sheet "net&sec"
是否只 ping 绿色单元格？(y/n，默认 n): n

============================================================
IP 地址规划表 Ping 工具
============================================================
文件: pass/IP地址规划表-金茂.xlsx
Sheet: net&sec
颜色过滤: 无
排除删除线: 是
============================================================

正在读取 pass/IP地址规划表-金茂.xlsx 的 net&sec sheet...
找到表头行: 第0行
MGMT 列索引: 11, hostname 列索引: 10
成功读取 194 个 IP 地址

找到 194 个 IP 地址:
  - 10.201.232.1    (spine1-502-I01-4-bj08)
  - 10.201.232.2    (spine2-504-I01-4-bj08)
  ...
```

## 命令行参数

### 必需参数

无，所有参数都有默认值。

### 可选参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--file` | `-f` | Excel 文件路径 | `pass/IP地址规划表-金茂.xlsx` |
| `--sheet` | `-s` | Sheet 页名称 | `net&sec` |
| `--color` | `-c` | 颜色过滤（green/none） | `none` |
| `--local` | - | 强制使用本地 ping | False |
| `--max-workers` | - | 并发数 | 自动（远程5，本地20） |
| `--list-colors` | - | 列出可用颜色 | - |
| `--no-exclude-strikethrough` | - | 不排除删除线 | False |

## 使用场景

### 场景 1：快速测试所有网络设备

```bash
# 默认配置，测试所有 net&sec 设备
ping-ip-planning
```

### 场景 2：只测试绿色标记的设备

```bash
# 方式 1：命令行指定
ping-ip-planning --color green

# 方式 2：交互式选择
ping-ip-planning
# 然后输入 y
```

### 场景 3：测试服务器和安全设备

```bash
ping-ip-planning --sheet "服务器&安全"
```

### 场景 4：本地高并发测试

```bash
# 使用本地 ping，30 个并发
ping-ip-planning --local --max-workers 30
```

### 场景 5：查看表格中使用的颜色

```bash
ping-ip-planning --list-colors
```

输出示例：
```
正在读取 pass/IP地址规划表-金茂.xlsx 的 net&sec sheet 中 MGMT 列的颜色...

找到 3 种颜色:
  - 92D050
  - C6EFCE
  - FF0000
```

## 输出说明

### 实时输出

测试过程中会显示实时进度：

```
开始 ping 测试...
------------------------------------------------------------
✓ 10.201.232.1    (spine1-502-I01-4-bj08         ) - 可达
✓ 10.201.232.2    (spine2-504-I01-4-bj08         ) - 可达
✗ 10.201.232.3    (GPU leaf1-1-502-B10-21-bj08   ) - 不可达
  进度: 3/194 (1.5%)
...
```

### 统计摘要

测试完成后显示统计信息：

```
============================================================
测试结果统计
============================================================
总计 IP 数量: 194
可达 IP 数量: 190
不可达 IP 数量: 4
可达率: 97.9%
============================================================
```

### 日志文件

详细结果会保存到日志文件：

- 位置：`logs/ping_results_net_sec.log` 或 `logs/ping_results_服务器_安全.log`
- 内容：完整的 ping 输出，包括延迟统计

日志文件结构：

```
IP 地址规划表 Ping 测试结果
============================================================
文件: pass/IP地址规划表-金茂.xlsx
Sheet: net&sec
测试来源: 198.18.0.1
颜色过滤: 无
排除删除线: 是
总计 IP: 194
可达 IP: 190
不可达 IP: 4
可达率: 97.9%
============================================================

可达的 IP (190):
------------------------------------------------------------

10.201.232.1 - spine1-502-I01-4-bj08
----------------------------------------
PING 10.201.232.1 (10.201.232.1): 56 data bytes
64 bytes from 10.201.232.1: icmp_seq=0 ttl=64 time=0.389 ms
64 bytes from 10.201.232.1: icmp_seq=1 ttl=64 time=0.312 ms
64 bytes from 10.201.232.1: icmp_seq=2 ttl=64 time=0.301 ms

--- 10.201.232.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 0.301/0.334/0.389/0.039 ms

...
```

## 故障排查

### 问题 1：无法读取 Excel 文件

**错误信息：**
```
错误: 文件不存在: pass/IP地址规划表-金茂.xlsx
```

**解决方法：**
1. 检查文件路径是否正确
2. 确保文件在 `pass/` 目录下
3. 使用 `--file` 参数指定完整路径

### 问题 2：无法读取样式信息

**警告信息：**
```
警告: 无法读取单元格样式信息: expected <class 'openpyxl.styles.fills.Fill'>
将跳过颜色和删除线过滤功能
```

**说明：**
- 这是 Excel 文件格式兼容性问题
- 数据仍然可以正常读取，只是无法过滤颜色和删除线
- 可以正常进行 ping 测试

**解决方法（可选）：**
1. 在 Excel 中打开文件，另存为新的 .xlsx 格式
2. 不使用颜色过滤功能（使用 `--color none`）

### 问题 3：找不到 sheet 页

**错误信息：**
```
ValueError: 在 xxx sheet 中未找到包含 'MGMT' 和 'hostname' 的表头行
```

**解决方法：**
1. 确认 sheet 名称拼写正确（区分大小写）
2. 确认 sheet 中有 `MGMT` 和 `hostname` 列
3. 使用 `pandas` 查看可用的 sheet：

```python
import pandas as pd
xls = pd.ExcelFile('pass/IP地址规划表-金茂.xlsx', engine='calamine')
print(xls.sheet_names)
```

### 问题 4：无法连接远程服务器

**提示信息：**
```
无法连接到服务器，将使用本地 ping
```

**说明：**
- 工具会自动降级为本地 ping
- 如果要强制使用本地，可以添加 `--local` 参数

## 高级用法

### 自定义并发数

根据网络环境和性能需求调整并发数：

```bash
# 低并发（更稳定）
ping-ip-planning --max-workers 5

# 高并发（更快速，需要好的网络）
ping-ip-planning --local --max-workers 50
```

### 结合 grep 过滤结果

```bash
# 只查看不可达的 IP
ping-ip-planning | grep "✗"

# 保存结果到文件
ping-ip-planning > results.txt 2>&1
```

### 批量测试多个 sheet

```bash
#!/bin/bash
for sheet in "net&sec" "服务器&安全"; do
    echo "Testing sheet: $sheet"
    ping-ip-planning --sheet "$sheet"
    echo "---"
done
```

## 注意事项

1. **Excel 文件格式**：
   - 推荐使用 .xlsx 格式
   - 确保文件未被其他程序占用
   - 建议定期备份

2. **颜色过滤限制**：
   - 目前仅支持绿色过滤
   - 某些 Excel 格式可能无法读取样式
   - 如果样式读取失败，会自动跳过过滤

3. **删除线处理**：
   - 默认排除删除线的 IP
   - 如需测试删除线的 IP，使用 `--no-exclude-strikethrough`

4. **并发性能**：
   - 本地 ping 推荐 20-30 并发
   - 远程 SSH 推荐 5-10 并发
   - 过高的并发可能导致连接失败

5. **日志文件**：
   - 每次运行会覆盖之前的日志
   - 如需保留历史记录，请手动备份
