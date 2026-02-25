# IP 地址规划表 Ping 工具使用指南

## 快速开始

### 1. 网段模式（快速扫描）

```bash
# 激活虚拟环境
cd /Users/sen/automate/Network_Projects/ethernet/ping
source .venv/bin/activate

# 直接 ping 一个网段
ping-ip-planning 192.168.1.0/24

# 指定并发数
ping-ip-planning 10.201.232.0/24 --max-workers 50
```

### 2. 交互式模式（Excel 规划表）

无参数时自动进入交互式流程：

```bash
$ ping-ip-planning

欢迎使用 IP 地址规划表 Ping 工具
======================================================================
1. 选择环境（金茂/xxidc/xx项目）
2. 选择 Sheet（network&security / server&security）
3. 选择列和 ping 模式
4. 是否颜色过滤

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

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `subnet` | - | CIDR 网段（位置参数，如 `192.168.1.0/24`） | 无（进入交互模式） |
| `--color` | `-c` | 颜色过滤（green/none） | 交互式选择 |
| `--local` | - | 强制使用本地 ping | 交互式选择 |
| `--max-workers` | - | 并发数 | 自动（本地30） |
| `--list-colors` | - | 列出可用颜色 | - |
| `--no-exclude-strikethrough` | - | 不排除删除线 | False |

## 使用场景

### 场景 1：快速扫描一个网段

```bash
# 直接传入 CIDR 网段
ping-ip-planning 192.168.254.0/24

# 大网段加大并发
ping-ip-planning 10.0.0.0/16 --max-workers 100
```

### 场景 2：使用 Excel 规划表测试

```bash
# 交互式模式
ping-ip-planning
# 然后选择：环境 -> Sheet -> 列 -> ping模式 -> 颜色过滤
```

### 场景 3：只测试绿色标记的设备

```bash
# 运行时强制过滤绿色
ping-ip-planning --color green
# 然后正常进行交互式选择
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

**⚠️ 重要提示：颜色过滤的前提条件**

颜色过滤功能需要 Excel 文件中的单元格有填充颜色：

1. **如果找到 0 种颜色**：
   ```
   找到 0 种颜色
   ```
   说明 MGMT 列的所有单元格都是无色的，此时：
   - ❌ 使用 `--color green` 将找不到任何 IP
   - ✅ 只能使用 `--color none`（不过滤）来 ping 所有 IP

2. **如何给单元格添加颜色**：
   - 在 Excel 中打开文件
   - 选中需要 ping 的 MGMT 列单元格
   - 点击"填充颜色"，选择绿色（或其他颜色）
   - 保存文件

3. **检查颜色是否生效**：
   ```bash
   ping-ip-planning --list-colors
   # 应该能看到颜色列表
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
