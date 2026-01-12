# 👶 完全新手指南 - 从零开始

> 如果你从来没有用过命令行，这份指南就是为你准备的！

---

## 🎯 目标

用这个工具测试网络设备是否能 ping 通。

---

## 📝 术语解释（给完全不懂的人）

- **终端/Terminal**：一个黑窗口，可以输入命令让电脑执行
- **命令**：告诉电脑做什么的指令
- **目录/文件夹**：存放文件的地方
- **路径**：文件在电脑里的位置，比如 `/Users/sen/Documents/文件.xlsx`
- **Excel 文件**：后缀是 `.xlsx` 的表格文件
- **虚拟环境**：一个独立的 Python 运行环境，不影响系统

---

## 🚀 开始使用（5 分钟上手）

### Step 1: 打开终端

**macOS**：
1. 按 `Command + 空格`
2. 输入 "Terminal"
3. 回车

**Windows**：
1. 按 `Windows 键 + R`
2. 输入 "cmd"
3. 回车

**Linux**：
1. 按 `Ctrl + Alt + T`

---

### Step 2: 进入项目目录

```bash
# 假设你把项目放在了 Documents 文件夹
cd ~/Documents/ping

# 检查是否进入正确
pwd
# 应该显示：/Users/你的用户名/Documents/ping
```

**💡 提示**：
- `cd` 是 "change directory" 的缩写，意思是"进入某个文件夹"
- `~` 代表你的用户主目录
- `pwd` 是 "print working directory"，显示当前位置

---

### Step 3: 一键安装（最重要的一步）

```bash
# 直接复制粘贴这一行，然后回车
python3 -m venv .venv && source .venv/bin/activate && pip3 install -r requirements.txt
```

**看到什么？**
```
Collecting pandas==2.3.3
Installing collected packages: ...
Successfully installed pandas-2.3.3 ...
```

✅ 看到 "Successfully installed" 就说明安装成功了！

❌ 如果出错，看本文档最后的"常见错误"部分

---

### Step 4: 准备测试文件

#### 选项 A：测试 IP 地址规划表（推荐）

```bash
# 1. 把你的 Excel 文件复制到 pass 文件夹
# 用鼠标拖拽文件到 pass/ 文件夹即可

# 2. 确认文件在那里
ls pass/
# 应该看到你的 Excel 文件名
```

#### 选项 B：使用示例文件（用于学习）

```bash
# 复制示例文件
cp examples/credentials.example.xlsx pass/credentials.xlsx

# 用 Excel 打开它，填入真实 IP
open pass/credentials.xlsx  # macOS
```

---

### Step 5: 开始测试！

**最简单的方式**：
```bash
ping-ip-planning
```

**然后你会看到**：
```
欢迎使用 IP 地址规划表 Ping 工具
======================================================================

Excel 文件路径: 
```

**按提示输入信息**：
1. 输入文件路径：`pass/你的文件.xlsx`
2. 选择 Sheet：输入 `1` 或 `2`
3. 是否过滤颜色：输入 `n`（不过滤）
4. 等待结果

---

## 📊 看结果

测试完成后：

```
============================================================
测试结果统计
============================================================
总计 IP 数量: 50
可达 IP 数量: 45
不可达 IP 数量: 5
可达率: 90.0%
============================================================
```

✅ **成功了！**

详细结果在 `logs/` 文件夹里，双击打开查看。

---

## 🎬 完整操作录屏示例

```
# 第 1 步：打开终端
# 第 2 步：
$ cd ~/Documents/ping
$ pwd
/Users/sen/Documents/ping

# 第 3 步：
$ python3 -m venv .venv && source .venv/bin/activate && pip3 install -r requirements.txt
Successfully installed pandas-2.3.3 openpyxl-3.1.5 paramiko-4.0.0 pyyaml-6.0

# 第 4 步：
$ ls pass/
IP地址规划表-金茂.xlsx

# 第 5 步：
$ ping-ip-planning

欢迎使用 IP 地址规划表 Ping 工具
======================================================================

Excel 文件路径: pass/IP地址规划表-金茂.xlsx
✓ 文件存在: pass/IP地址规划表-金茂.xlsx

选择要测试的 Sheet 页:
======================================================================
  1. network&security（网络和安全）
  2. server&security（服务器和安全）
======================================================================

请选择 Sheet（必选，输入 q 退出）: 1

是否只 ping 绿色单元格？(y/n) [n]: n

开始 ping 测试...
✓ 10.0.0.1    (router-01) - 可达
✓ 10.0.0.2    (switch-01) - 可达
✗ 10.0.0.3    (server-01) - 不可达
...

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

---

## ❌ 常见错误及解决

### 错误 1：command not found: python3

**原因**：没有安装 Python

**解决**：
1. 访问 https://www.python.org/downloads/
2. 下载并安装 Python 3.8 或更高版本
3. 重启终端再试

---

### 错误 2：command not found: ping-ip-planning

**原因**：没有激活虚拟环境

**解决**：
```bash
# 每次打开新终端都要执行这个
source .venv/bin/activate

# 提示符会变成：
(.venv) $
```

---

### 错误 3：FileNotFoundError: 'pass/xxx.xlsx'

**原因**：文件路径不对

**解决**：
```bash
# 1. 检查文件在哪
ls pass/

# 2. 使用正确的文件名（包括中文、空格等）
# 如果文件名有空格，用引号括起来：
ping-ip-planning --file "pass/IP 规划表.xlsx"
```

---

### 错误 4：Permission denied

**原因**：没有权限

**解决**：
```bash
# 给文件加权限
chmod +x ping.py

# 或使用 sudo
sudo python3 ping.py
```

---

## 🎓 进阶：记住这些常用命令

```bash
# 进入项目目录
cd ~/Documents/ping

# 激活虚拟环境（每次必做）
source .venv/bin/activate

# 运行测试（最简单）
ping-ip-planning

# 查看日志
ls logs/

# 退出虚拟环境
deactivate
```

---

## 📱 创建桌面快捷方式（可选）

### macOS 用户：

创建 `Ping测试.command` 文件：
```bash
#!/bin/bash
cd ~/Documents/ping
source .venv/bin/activate
ping-ip-planning
```

然后：
1. 保存到桌面
2. 右键 → 打开方式 → 终端
3. 以后双击就能用

---

### Windows 用户：

创建 `Ping测试.bat` 文件：
```batch
@echo off
cd C:\Users\你的用户名\Documents\ping
call .venv\Scripts\activate
ping-ip-planning
pause
```

双击运行即可。

---

## ✅ 成功检查清单

- [ ] 能打开终端
- [ ] 能进入项目目录（`cd` 命令）
- [ ] 成功安装依赖（看到 "Successfully installed"）
- [ ] 能激活虚拟环境（提示符有 `.venv`）
- [ ] 能运行 `ping-ip-planning`
- [ ] 能看到测试结果
- [ ] 能找到日志文件

全部打勾？🎉 恭喜你学会了！

---

## 🆘 还是不行？

1. **截图错误信息**
2. **记录你执行的命令**
3. **联系项目维护者**或提交 Issue

提供信息：
- 操作系统（macOS/Windows/Linux）
- Python 版本（`python3 --version`）
- 错误截图
- 你执行的完整命令

---

## 🎉 下一步

会用了？太棒了！可以：

- 阅读 [QUICKSTART.md](../QUICKSTART.md) 了解更多用法
- 尝试其他功能（从服务器 ping、延迟分析等）
- 看看 [README.md](../README.md) 的完整文档

---

**记住**：
- 每次使用前要激活虚拟环境
- 遇到问题先看错误提示
- 不要害怕终端，它只是一个工具
