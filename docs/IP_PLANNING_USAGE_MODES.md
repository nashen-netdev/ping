# IP 地址规划表 Ping 工具 - 使用模式说明

本工具支持三种使用模式，适合不同技术水平的用户使用。

---

## 📋 三种使用模式

### 模式 1：配置文件模式（推荐给普通用户）

**适用场景**：
- 不懂技术的普通用户
- 经常需要重复执行相同的测试
- 需要快速切换不同的测试场景

**使用方法**：

```bash
# 1. 查看可用的配置环境
ping-ip-planning --list-profiles

# 输出示例：
# 可用的配置环境:
# ======================================================================
#   • default              - 默认配置: 金茂项目网络设备 ping 测试
#   • network_devices      - 网络设备: 只 ping 网络和安全设备
#   • servers              - 服务器设备: 只 ping 服务器和安全设备
#   • green_only           - 绿色标记设备: 只 ping 标记为绿色的设备
#   • local_fast           - 本地高速测试: 使用本地 ping，高并发
# ======================================================================

# 2. 使用指定的配置环境
ping-ip-planning --profile network_devices
ping-ip-planning --profile servers
ping-ip-planning --profile local_fast

# 3. 简写方式
ping-ip-planning -p default
```

**配置文件位置**：
```
configs/ip_planning_profiles.yaml
```

**如何添加新的配置**：

编辑 `configs/ip_planning_profiles.yaml`，添加新的配置：

```yaml
# 你的自定义配置
my_custom:
  name: "我的自定义配置"
  description: "测试特定区域的设备"
  file: "pass/IP地址规划表-金茂1.xlsx"
  sheet: "net&sec"
  color_filter: "none"  # none, green
  exclude_strikethrough: true
  use_local: false
  max_workers: 10
```

---

### 模式 2：交互式模式（最简单）

**适用场景**：
- 第一次使用工具
- 不记得命令参数
- 需要一步步确认配置

**使用方法**：

```bash
# 方式 1：直接运行（无参数自动进入交互模式）
ping-ip-planning

# 方式 2：明确指定交互模式
ping-ip-planning --interactive
ping-ip-planning -i
```

**交互流程**：

```
欢迎使用 IP 地址规划表 Ping 工具
======================================================================

可用的配置环境:
======================================================================
  1. [default] 默认配置: 金茂项目网络设备 ping 测试
  2. [network_devices] 网络设备: 只 ping 网络和安全设备
  3. [servers] 服务器设备: 只 ping 服务器和安全设备
  4. [green_only] 绿色标记设备: 只 ping 标记为绿色的设备
  5. [local_fast] 本地高速测试: 使用本地 ping，高并发

  0. 不使用配置，手动输入参数
======================================================================

请选择配置环境（输入序号，回车使用默认）: 1

✓ 已选择配置: default

[然后开始 ping 测试...]
```

**如果选择手动输入（输入 0）**：

```
======================================================================
交互式配置
======================================================================
提示: 直接回车使用默认值，输入 'q' 或 Ctrl+C 退出

Excel 文件路径 [pass/IP地址规划表-金茂1.xlsx]: 
✓ 文件存在: pass/IP地址规划表-金茂1.xlsx

Sheet 页名称 [net&sec]: 

颜色过滤 (green/none) [none]: 

排除删除线的 IP? (y/n) [y]: 

使用本地 ping? (y/n) [n]: 

并发数 (留空自动) [auto]: 

======================================================================
配置确认:
======================================================================
  文件: pass/IP地址规划表-金茂1.xlsx
  Sheet: net&sec
  颜色过滤: none
  排除删除线: 是
  本地 ping: 否
  并发数: 自动
======================================================================

确认以上配置? (y/n) [y]: y

[然后开始 ping 测试...]
```

---

### 模式 3：命令行模式（适合技术用户）

**适用场景**：
- 熟悉命令行的技术用户
- 需要在脚本中自动化执行
- 需要临时修改某些参数

**使用方法**：

```bash
# 基本用法
ping-ip-planning --file pass/IP地址规划表-金茂1.xlsx --sheet "net&sec"

# 完整参数
ping-ip-planning \
    --file pass/IP地址规划表-金茂1.xlsx \
    --sheet "net&sec" \
    --color none \
    --local \
    --max-workers 20

# 简写方式
ping-ip-planning -f pass/IP地址规划表-金茂1.xlsx -s "net&sec" -c none

# 只 ping 绿色单元格
ping-ip-planning -f pass/IP地址规划表-金茂1.xlsx -s "net&sec" -c green

# 本地高并发测试
ping-ip-planning -f pass/IP地址规划表-金茂1.xlsx -s "net&sec" --local --max-workers 30
```

**所有参数说明**：

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--file` | `-f` | Excel 文件路径 | `pass/IP地址规划表-金茂1.xlsx` |
| `--sheet` | `-s` | Sheet 页名称 | `net&sec` |
| `--color` | `-c` | 颜色过滤（green/none） | `none` |
| `--no-exclude-strikethrough` | - | 不排除删除线 | False（默认排除） |
| `--local` | - | 使用本地 ping | False（默认远程） |
| `--max-workers` | - | 并发数 | 自动（远程5，本地20） |
| `--list-colors` | - | 列出可用颜色 | - |
| `--profile` | `-p` | 使用配置环境 | - |
| `--interactive` | `-i` | 交互式模式 | - |
| `--list-profiles` | - | 列出配置环境 | - |

---

## 🎯 使用场景示例

### 场景 1：普通用户日常使用

**小王（网络管理员，不懂 Python）**

```bash
# 每天早上检查网络设备
ping-ip-planning --profile network_devices

# 或者直接运行，然后选择配置
ping-ip-planning
# 输入: 2  (选择 network_devices)
```

### 场景 2：临时测试

**小李（技术支持，需要临时测试）**

```bash
# 直接运行，进入交互模式
ping-ip-planning

# 选择 0（手动输入）
# 然后按提示输入文件路径和参数
```

### 场景 3：自动化脚本

**小张（运维工程师，需要自动化）**

```bash
#!/bin/bash
# 每小时自动检查网络设备

cd /path/to/ping
source .venv/bin/activate

# 使用配置文件
ping-ip-planning --profile network_devices > /var/log/network_check.log

# 或使用命令行参数
ping-ip-planning \
    --file pass/IP地址规划表-金茂1.xlsx \
    --sheet "net&sec" \
    --local \
    --max-workers 30
```

### 场景 4：多环境切换

**小赵（项目经理，管理多个项目）**

```bash
# 上午测试网络设备
ping-ip-planning --profile network_devices

# 下午测试服务器
ping-ip-planning --profile servers

# 晚上做全面检查
ping-ip-planning --profile local_fast
```

---

## 💡 最佳实践

### 给普通用户的建议

1. **第一次使用**：
   ```bash
   ping-ip-planning --list-profiles  # 查看可用配置
   ping-ip-planning --profile default  # 使用默认配置
   ```

2. **日常使用**：
   - 记住常用的配置名称（如 `network_devices`）
   - 直接运行 `ping-ip-planning --profile network_devices`

3. **遇到问题**：
   - 使用交互模式：`ping-ip-planning --interactive`
   - 一步步确认每个参数

### 给技术用户的建议

1. **创建自己的配置**：
   - 编辑 `configs/ip_planning_profiles.yaml`
   - 添加常用的配置环境

2. **在脚本中使用**：
   ```bash
   # 使用配置文件（推荐）
   ping-ip-planning --profile my_config
   
   # 或使用命令行参数
   ping-ip-planning -f file.xlsx -s sheet -c none
   ```

3. **组合使用**：
   ```bash
   # 使用配置，但覆盖某些参数
   ping-ip-planning --profile default --local --max-workers 50
   ```

---

## 🔧 配置文件详解

### 配置文件结构

```yaml
配置名称:
  name: "显示名称"
  description: "配置说明"
  file: "Excel 文件路径"
  sheet: "Sheet 页名称"
  color_filter: "颜色过滤（none/green）"
  exclude_strikethrough: true/false  # 是否排除删除线
  use_local: true/false  # 是否使用本地 ping
  max_workers: 数字或null  # 并发数（null 表示自动）
```

### 配置示例

```yaml
# 快速测试配置
quick_test:
  name: "快速测试"
  description: "本地高并发，快速完成测试"
  file: "pass/IP地址规划表-金茂1.xlsx"
  sheet: "net&sec"
  color_filter: "none"
  exclude_strikethrough: true
  use_local: true
  max_workers: 50

# 只测试重要设备
important_only:
  name: "重要设备"
  description: "只测试标记为绿色的重要设备"
  file: "pass/IP地址规划表-金茂1.xlsx"
  sheet: "net&sec"
  color_filter: "green"
  exclude_strikethrough: true
  use_local: false
  max_workers: 10
```

---

## ❓ 常见问题

### Q1: 如何让普通用户使用？

**A**: 最简单的方式：
1. 创建桌面快捷方式或脚本
2. 双击运行，自动进入交互模式
3. 按提示选择配置即可

### Q2: 配置文件放在哪里？

**A**: `configs/ip_planning_profiles.yaml`

### Q3: 如何添加新配置？

**A**: 编辑配置文件，按照示例格式添加即可

### Q4: 交互模式可以退出吗？

**A**: 可以，输入 `q` 或按 `Ctrl+C` 退出

### Q5: 命令行参数会覆盖配置吗？

**A**: 是的，命令行参数优先级最高

---

## 📚 相关文档

- [基础使用文档](IP_PLANNING_USAGE.md)
- [项目 README](../README.md)
- [安装指南](INSTALL.md)
