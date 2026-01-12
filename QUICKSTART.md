# 🚀 零基础快速入门指南

> 本指南专为**完全不懂编程**的用户设计，跟着步骤做就能用！

---

## 📋 使用前准备

### 1. 检查电脑是否有 Python

**macOS/Linux 用户**：
```bash
# 打开终端（Terminal），输入：
python3 --version

# 如果显示类似 "Python 3.8.10" 就说明已安装
# 如果没有，请先安装 Python（见下文）
```

**Windows 用户**：
```bash
# 打开命令提示符（CMD），输入：
python --version

# 如果显示类似 "Python 3.8.10" 就说明已安装
```

### 2. 如果没有 Python，先安装

- **macOS**: 访问 https://www.python.org/downloads/ 下载安装
- **Windows**: 访问 https://www.python.org/downloads/ 下载安装
- **Linux**: `sudo apt install python3` (Ubuntu/Debian) 或 `sudo yum install python3` (CentOS)

---

## 📥 第一步：下载项目

### 方法 1：使用 Git（推荐）
```bash
# 1. 打开终端
# 2. 进入你想保存项目的目录，例如：
cd ~/Documents

# 3. 克隆项目
git clone <项目地址>

# 4. 进入项目目录
cd ping
```

### 方法 2：直接下载 ZIP
1. 在项目页面点击 "Download ZIP"
2. 解压到某个目录
3. 用终端进入该目录

---

## ⚙️ 第二步：安装项目

**推荐：一键安装脚本**（最简单）
```bash
# 在项目目录下，执行：
make install

# 如果提示 make 命令不存在，使用下面的方法
```

**备用：手动安装**
```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 3. 安装依赖
pip3 install -r requirements.txt
```

---

## 🎯 第三步：选择使用场景

根据你的需求选择对应的工具：

### 场景 A：测试 IP 地址规划表（最常用）✨

**适用于**：你有一个 Excel 格式的 IP 地址规划表

**使用方法**：
```bash
# 1. 把你的 Excel 文件放到 pass/ 目录下
cp /path/to/你的规划表.xlsx pass/

# 2. 运行工具（交互式，最简单）
ping-ip-planning

# 3. 按提示操作：
#    - 选择环境（或按回车跳过）
#    - 输入 Excel 文件路径
#    - 选择要测试的 Sheet 页
#    - 选择是否过滤颜色
#    - 等待结果
```

**示例**：
```
欢迎使用 IP 地址规划表 Ping 工具
======================================================================

进入手动输入模式...
======================================================================

Excel 文件路径: pass/IP地址规划表.xlsx
✓ 文件存在: pass/IP地址规划表.xlsx

选择要测试的 Sheet 页:
======================================================================
  1. network&security（网络和安全）
  2. server&security（服务器和安全）
======================================================================

请选择 Sheet（必选，输入 q 退出）: 1
✓ 已选择: network&security

是否只 ping 绿色单元格？(y/n) [n]: n
✓ 不过滤颜色，ping 所有设备

[开始测试...]
```

---

### 场景 B：测试 credentials.xlsx 中的设备

**适用于**：你有一个 credentials.xlsx 凭证文件

**准备工作**：
```bash
# 1. 复制示例文件
cp examples/credentials.example.xlsx pass/credentials.xlsx

# 2. 用 Excel 打开 pass/credentials.xlsx
# 3. 填入你的 IP 地址和凭证信息
# 4. 保存文件
```

**运行测试**：
```bash
# 方式 1：使用 Makefile
make run

# 方式 2：直接运行
python3 ping.py
```

---

## 📊 第四步：查看结果

测试完成后，结果保存在 `logs/` 目录：

```bash
# 查看日志文件
ls logs/

# 可能的日志文件：
# - ping_results.log                      # 标准工具的结果
# - ping_results_network_security.log    # IP 规划表测试结果
# - ping_results_server_security.log     # 服务器测试结果
```

**用文本编辑器打开查看**：
```bash
# macOS:
open logs/ping_results_network_security.log

# Linux:
gedit logs/ping_results_network_security.log

# Windows:
notepad logs\ping_results_network_security.log
```

---

## 🎓 第五步：进阶使用（可选）

### 快速添加新的测试环境

```bash
# 为新项目创建配置
ping-env-add 项目名 /path/to/规划表.xlsx --display-name "项目显示名称"

# 例如：
ping-env-add bj08 pass/IP规划表-北京.xlsx --display-name "北京08机房"
```

### 查看所有可用命令

```bash
# 查看帮助
ping-ip-planning --help

# 列出所有环境
ping-ip-planning --list-profiles

# 查看版本
python3 -c "import ping_tool; print(ping_tool.__version__)"
```

---

## ❓ 常见问题

### Q1: 提示 "command not found: ping-ip-planning"

**原因**：没有激活虚拟环境

**解决**：
```bash
# 先激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 然后再运行命令
ping-ip-planning
```

### Q2: 提示 "No module named 'pandas'"

**原因**：依赖没有安装

**解决**：
```bash
pip3 install -r requirements.txt
```

### Q3: 找不到 Excel 文件

**原因**：文件路径不对

**解决**：
```bash
# 确保文件在 pass/ 目录下
ls pass/

# 或使用绝对路径
ping-ip-planning --file /完整路径/到/你的文件.xlsx
```

### Q4: 测试结果在哪里？

**答案**：在 `logs/` 目录下

```bash
# 查看所有日志
ls -lh logs/

# 查看最新的日志
ls -lt logs/ | head -5
```

### Q5: 如何退出虚拟环境？

```bash
deactivate
```

---

## 🔧 故障排查

### 如果遇到错误，按以下顺序检查：

1. **检查 Python 版本**：
   ```bash
   python3 --version  # 应该是 3.8 或更高
   ```

2. **检查是否激活虚拟环境**：
   ```bash
   which python3
   # 应该显示类似：/path/to/ping/.venv/bin/python3
   ```

3. **重新安装依赖**：
   ```bash
   pip3 install --upgrade -r requirements.txt
   ```

4. **清理并重新安装**：
   ```bash
   make clean
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   make install
   ```

---

## 📞 获取帮助

如果以上步骤都无法解决问题：

1. **查看详细文档**：
   - [README.md](README.md) - 项目总览
   - [docs/INSTALL.md](docs/INSTALL.md) - 安装指南
   - [docs/TOOLS_COMPARISON.md](docs/TOOLS_COMPARISON.md) - 工具对比

2. **查看示例**：
   - [examples/README.md](examples/README.md) - 示例文件说明

3. **提交 Issue**：
   在项目页面提交问题，描述：
   - 你的操作系统
   - 错误信息截图
   - 你执行的命令

---

## 🎉 成功标志

当你看到类似以下输出时，说明运行成功：

```
============================================================
测试结果统计
============================================================
总计 IP 数量: 50
可达 IP 数量: 48
不可达 IP 数量: 2
可达率: 96.0%
============================================================

详细结果已写入: logs/ping_results_network_security.log
程序执行完成！
```

恭喜！🎊 你已经成功使用了这个工具！

---

## 📚 下一步

- 阅读 [README.md](README.md) 了解更多功能
- 尝试不同的测试场景
- 探索高级功能（从服务器 ping、延迟分析等）

---

**记住**：遇到问题不要慌，按照故障排查步骤一步步来！
