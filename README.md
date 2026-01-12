# 网络 Ping 测试工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-orange)](https://github.com/yourorg/ping-tool)

一个专业的网络连通性测试工具，采用标准Python项目架构，支持本地和远程并发测试。

## 快速开始

### 安装

```bash
# 方法1：开发模式安装（推荐）
cd /path/to/ping
python3 -m venv .venv
source .venv/bin/activate
make install

# 方法2：直接使用
pip3 install -r requirements.txt
python3 ping.py
```

### 基础使用

```bash
# 使用Makefile运行
make run

# 或作为Python模块运行
python3 -m ping_tool

# 或使用命令行工具（需先安装）
ping-tool

# 或使用兼容脚本
python3 ping.py

# 使用 IP 地址规划表 Ping 工具
ping-ip-planning --file pass/IP地址规划表-金茂.xlsx --sheet "net&sec"
```

### IP 地址规划表 Ping 功能（新功能）

专门用于 ping IP 地址规划表中的设备，支持三步式交互流程：

```bash
# 方式 1：交互式模式（推荐，最简单）
ping-ip-planning
# 1. 选择环境（金茂/xxidc/xx项目）
# 2. 选择 Sheet（network&security / server&security）
# 3. 是否颜色过滤

# 方式 2：命令行模式
ping-ip-planning --file pass/IP地址规划表-金茂.xlsx --sheet "network&security"

# 列出所有可用环境
ping-ip-planning --list-profiles

# 查看可用的颜色
ping-ip-planning --list-colors
```

**功能特性：**
- ✅ **三步式交互流程**：选择环境 → 选择 Sheet → 颜色过滤
- ✅ **环境配置管理**：独立的环境配置文件，易于维护
- ✅ 自动读取 MGMT 列的 IP 地址和 hostname
- ✅ 支持按颜色过滤（绿色等，需要 Excel 格式支持）
- ✅ 自动排除删除线的 IP 地址
- ✅ 支持本地或远程 ping
- ✅ **🆕 从服务器 ping**：登录到指定服务器，从该服务器ping其他设备（server&security 专用）
- ✅ **延迟质量分析**：自动分析 RTT（min/avg/max/mdev），识别高延迟 IP
- ✅ 生成详细的测试报告（IP + hostname + 延迟统计）
- ✅ 自动统计可达率

**环境配置：**

环境配置文件位于 `env/` 目录，每个项目一个 YAML 文件：

```yaml
# env/jinmao.yaml
name: "金茂"
file: "pass/IP地址规划表-金茂1.xlsx"
```

**快速添加新环境：**

```bash
# 使用命令快速创建（推荐）
ping-env-add bj08 /path/to/file.xlsx

# 指定显示名称
ping-env-add bj08 /path/to/file.xlsx --display-name "北京08机房"
```

详见 [env/README.md](env/README.md)

详细安装说明请查看 [docs/INSTALL.md](docs/INSTALL.md)

## 📚 项目文档

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目主文档（本文件） |
| [INSTALL.md](docs/INSTALL.md) | 安装指南 |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | 开发指南 |
| [TESTING.md](docs/TESTING.md) | 测试文档（86%覆盖率） |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 架构设计文档 |
| [CHANGELOG.md](CHANGELOG.md) | 版本变更记录 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [LICENSE](LICENSE) | MIT开源许可证 |

## 快速功能一览

| 功能分类 | 支持特性 |
|---------|---------|
| **输入支持** | Excel配置文件、单个IP、CIDR网段、跳板机配置、IP地址规划表 |
| **执行模式** | 本地测试、远程SSH测试、自动模式切换 |
| **认证方式** | SSH密码认证、SSH密钥认证 |
| **并发性能** | 本地20-30线程、远程5线程、智能调整 |
| **延迟分析** | Min/Avg/Max/Mdev统计、高延迟识别、排序分析 |
| **进度反馈** | 实时百分比、成功/失败标记、统计汇总 |
| **日志输出** | 总计统计、延迟分析、详细结果、分类记录 |
| **容错机制** | 连接重试、自动降级、异常处理、空值处理 |

## 功能特点

### 核心功能
- ✅ 支持单个IP地址或整个网段（CIDR表示法）的Ping测试
- ✅ 智能执行模式：可在本地或通过远程服务器运行测试
- ✅ 自动服务器识别：通过Excel中的`server`列自动识别跳板机
- ✅ 双认证模式：支持SSH密码认证和密钥认证

### 高性能并发执行
- **本地测试**：
  - 单个IP：20个并发线程
  - 网段：30个并发线程
- **远程测试**：
  - 单个IP：5个并发线程（避免SSH连接限制）
  - 网段：5个并发线程
  - 每个线程独立SSH连接，真正实现并发
- **优化参数**：`-c 3 -W 2 -i 0.2`（3个包，2秒超时，0.2秒间隔）

### 智能分析功能
- ✅ 延迟质量分析：
  - 提取最小/平均/最大/抖动（mdev）延迟值
  - 自动识别高延迟连接（最大RTT > 1ms）
  - 按延迟从高到低排序，便于优先处理
- ✅ 自动IP分类处理：
  - 智能区分单个IP和网段
  - 从目标列表中自动排除服务器IP
  - 防止自己ping自己造成干扰

### 健壮性保障
- ✅ Excel数据类型处理：
  - 自动将用户名、密码转换为字符串
  - 智能处理整数密码（去除.0后缀）
  - 兼容pd.notna空值检查
- ✅ SSH连接重试机制：
  - 最多重试2次
  - 递增延迟（0.5秒 × 重试次数）
  - 自动禁用详细日志，减少错误干扰
- ✅ 容错处理：连接失败自动降级为本地测试

### 输出与报告
- ✅ 实时进度反馈：
  - 百分比进度显示
  - 成功/失败状态标记（✓/✗）
  - 实时显示最新完成的IP
- ✅ 详细日志记录：
  - 总计统计（总数、可达、不可达、高延迟）
  - 延迟质量分析专区
  - 完整的ping输出结果
  - 按来源IP分类记录

## 项目结构（标准Python架构）

```
ping/
├── README.md               # 📄 项目主文档
├── CHANGELOG.md            # 📄 版本变更记录
├── CONTRIBUTING.md         # 📄 贡献指南
├── LICENSE                 # 📄 MIT许可证
├── pyproject.toml          # 项目配置（PEP 621）
├── Makefile                # 快捷命令
├── requirements.txt        # 依赖列表
├── ping.py                 # 兼容性入口脚本
│
├── src/                    # 源代码（src-layout）
│   └── ping_tool/          # 主包
│       ├── __init__.py     # 包初始化
│       ├── __main__.py     # 模块入口
│       ├── cli.py          # CLI主程序
│       ├── core/           # 核心功能
│       │   ├── ping.py     # Ping功能实现
│       │   └── ssh.py      # SSH连接管理
│       ├── utils/          # 工具函数
│       │   ├── analysis.py # 延迟分析
│       │   ├── credentials.py # 凭证管理
│       │   └── network.py  # 网络工具
│       └── models/         # 数据模型（预留）
│
├── tests/                  # 单元测试（86%覆盖率）
│   ├── test_ping.py        # Ping功能测试
│   ├── test_ssh.py         # SSH连接测试
│   ├── test_credentials.py # 凭证管理测试
│   ├── test_analysis.py    # 延迟分析测试
│   └── test_network.py     # 网络工具测试
│
├── docs/                   # 📚 详细文档
│   ├── INSTALL.md          # 安装指南
│   ├── DEVELOPMENT.md      # 开发指南
│   ├── TESTING.md          # 测试文档
│   ├── ARCHITECTURE.md     # 架构设计
│   └── history/            # 历史记录
│       ├── REFACTORING_SUMMARY.md
│       └── SHORT_TERM_OPTIMIZATION.md
│
├── examples/               # ⭐ 示例文件
│   ├── credentials.example.xlsx  # Excel配置示例
│   └── README.md           # 示例说明文档
│
├── configs/                # 配置文件
│   └── config.yaml
│
├── logs/                   # 日志输出
│   └── ping_results.log
│
├── pass/                   # 凭证和密钥（不提交Git）
│   ├── credentials.xlsx    # SSH凭证（gitignore）
│   └── key/                # SSH密钥文件（gitignore）
│
└── .github/                # GitHub配置
    ├── ISSUE_TEMPLATE/     # Issue模板
    └── pull_request_template.md
```

**架构特点**：
- ✅ 采用 **src-layout** 标准结构
- ✅ 完整的 **pyproject.toml** 配置
- ✅ 模块化设计，职责分离
- ✅ 支持 `pip install -e .` 开发模式
- ✅ 支持 `python -m ping_tool` 模块运行
- ✅ 完善的测试框架

## 使用方法

工具提供两种主要使用方式：

### 1. 标准 Ping 工具（从 credentials.xlsx）

从Excel文件读取IP地址和凭证，可以从本地或远程服务器执行Ping测试。

```bash
# 使用 Makefile
make run

# 直接运行
python3 -m ping_tool

# 或使用命令行工具
ping-tool
```

### 2. IP 地址规划表 Ping 工具（新功能）

专门用于 ping IP 地址规划表中的网络设备。

```bash
# 基本用法
ping-ip-planning --file pass/IP地址规划表-金茂.xlsx --sheet "net&sec"

# 完整参数说明
ping-ip-planning \
    --file pass/IP地址规划表-金茂.xlsx \  # Excel 文件路径
    --sheet "net&sec" \                    # Sheet 页名称
    --color green \                        # 只 ping 绿色单元格（可选）
    --local \                              # 使用本地 ping（不使用远程）
    --max-workers 10                       # 并发数

# 其他有用的命令
ping-ip-planning --list-colors            # 列出可用的颜色
ping-ip-planning --sheet "服务器&安全"      # ping 其他 sheet
```

#### IP 地址规划表功能说明

**支持的 Sheet 页：**
- `net&sec` - 网络和安全设备
- `服务器&安全` - 服务器和安全设备

**功能特性：**
- ✅ 自动读取 `MGMT` 列的 IP 地址
- ✅ 同时读取 `hostname` 列，结果显示 "IP (hostname)"
- ✅ 自动排除删除线的 IP 地址（默认开启）
- ✅ 支持按颜色过滤（如只 ping 绿色单元格）
- ✅ 支持本地或远程 ping
- ✅ **🆕 从服务器 ping（server&security 专用）**：
  - 提供 hostname 或管理网IP地址
  - 自动从 Excel 中查找该服务器的 System User 和 System Password
  - 使用这些凭据登录到该服务器
  - 从该服务器 ping 其他目标设备
  - 适用于需要从特定服务器测试网络连通性的场景
- ✅ 生成详细的测试报告

**颜色过滤说明：**
- 工具会尝试读取 Excel 单元格的颜色信息
- 如果 Excel 文件格式不兼容，会跳过颜色过滤
- 使用 `--list-colors` 可以查看文件中使用的颜色
- 目前支持的颜色：`green`（绿色）

**输出示例：**
```
✓ 10.201.232.1    (spine1-502-I01-4-bj08         ) - 可达
✓ 10.201.232.2    (spine2-504-I01-4-bj08         ) - 可达
✗ 10.201.232.3    (GPU leaf1-1-502-B10-21-bj08   ) - 不可达
  进度: 3/194 (1.5%)

============================================================
测试结果统计
============================================================
总计 IP 数量: 194
可达 IP 数量: 190
不可达 IP 数量: 4
可达率: 97.9%
```

**日志文件：**
- 标准工具：`logs/ping_results.log`
- IP 规划表工具：`logs/ping_results_net_sec.log`

## 输入格式

### Excel配置文件说明

**快速开始**：使用示例文件
```bash
# 复制示例文件
cp examples/credentials.example.xlsx pass/credentials.xlsx

# 编辑填写真实凭证
vim pass/credentials.xlsx  # 或使用Excel打开
```

完整配置说明请查看 [examples/README.md](examples/README.md)

---

创建Excel文件`pass/credentials.xlsx`，包含以下列：

| 列名 | 说明 | 示例 | 必填 |
|-----|------|------|------|
| `IP` | IP地址或网段（CIDR） | `192.168.1.1` 或 `10.0.0.0/24` | ✅ 是 |
| `user` | SSH用户名（仅服务器需要） | `root` 或 `admin` | 服务器必填 |
| `pass` | SSH密码（可选，优先使用密钥） | `password123` 或 `123456` | 可选 |
| `server` | 是否为跳板机服务器 | `1`（是） 或 `0`（否） | ✅ 是 |

### 配置示例

```
IP              user    pass        server
10.201.96.12    root    mypass123   1        # 跳板机服务器
192.168.1.1     -       -           0        # 目标IP
192.168.1.2     -       -           0        # 目标IP
10.0.0.0/24     -       -           0        # 目标网段
```

### 重要说明

1. **服务器识别**：
   - `server=1`的IP会被识别为跳板机
   - 跳板机会被自动排除在测试目标之外
   - 只使用第一个找到的跳板机

2. **认证方式**：
   - **密码认证**：填写`pass`列
   - **密钥认证**：留空`pass`列，密钥文件放在`pass/key/{username}`
   - 密钥认证优先级更高

3. **数据类型**：
   - 整数密码（如`123456`）会自动转换为字符串
   - 自动去除`.0`后缀（Excel数字格式问题）
   - 空值会被正确处理为None

4. **网段格式**：
   - 支持CIDR表示法：`192.168.1.0/24`
   - 会自动展开为所有主机IP（排除网络地址和广播地址）

## 输出格式

### 日志文件结构

工具在`log/ping_results.log`中生成详细的日志文件，包含以下部分：

#### 1. 总计统计信息
```
总计统计信息:
----------------------------------------
测试来源: 10.201.96.12
总计ping的IP数量: 87
总计可达IP数量: 70
总计不可达IP数量: 17
延迟质量较差IP数量: 5 (最大RTT > 1ms)
----------------------------------------
```

#### 2. 延迟质量分析
按最大延迟从高到低排序，列出所有高延迟IP：
```
延迟质量分析:
----------------------------------------
以下IP的最大响应时间超过1ms:

IP: 192.168.1.100
  最小延迟: 0.850 ms
  平均延迟: 1.120 ms
  最大延迟: 2.450 ms
  延迟抖动: 0.320 ms
--------------------
```

#### 3. 详细Ping结果
- **单个IP结果**：分可达和不可达两部分
- **网段结果**：按网段分组，每个网段单独统计
- **完整输出**：包含ping命令的原始输出

### 控制台输出

实时显示执行进度：
```
正在读取 credentials.xlsx 文件...
成功读取 88 个IP地址
找到 1 个服务器IP
成功读取 87 个目标IP地址
使用服务器IP: 10.201.96.12
测试来源IP: 10.201.96.12

开始从远程服务器并发处理 87 个单独IP（并发数: 5，每个IP使用独立SSH连接）...
单个IP进度: 1/87 (1.1%) - 最新: 10.201.96.1 ✓
单个IP进度: 2/87 (2.3%) - 最新: 10.201.96.2 ✓
...
单个IP处理完成！可达: 70, 不可达: 17
```

## 技术实现分析

### 核心技术栈

| 技术 | 用途 | 说明 |
|-----|------|------|
| `pandas` | Excel文件处理 | 读取配置文件，处理数据类型 |
| `paramiko` | SSH连接 | 远程服务器认证和命令执行 |
| `subprocess` | 本地ping | 执行系统ping命令 |
| `ThreadPoolExecutor` | 并发控制 | 多线程并发执行ping任务 |
| `ipaddress` | 网段处理 | 解析CIDR，生成IP列表 |
| `socket` | 网络工具 | 获取本地IP地址 |

### 关键功能实现

1. **Excel配置读取**：
   - 使用`pd.read_excel()`读取配置
   - 自动类型转换（密码、用户名转字符串）
   - 智能处理整数密码的`.0`后缀问题
   - 使用`pd.notna()`正确处理空值

2. **智能服务器识别**：
   - 遍历所有IP，识别`server=1`的跳板机
   - 自动排除跳板机，避免自己ping自己
   - 支持无服务器模式（自动降级为本地测试）

3. **SSH连接池机制**：
   ```python
   class SSHConnectionPool:
       - 每个线程创建独立SSH连接
       - 带重试机制（最多2次）
       - 递增延迟避免连接风暴
       - 自动关闭连接避免泄漏
   ```

4. **并发架构**：
   - 使用`ThreadPoolExecutor`管理线程池
   - `as_completed()`实时获取完成结果
   - 智能调整并发数（本地20，远程5）
   - 单个IP和网段分别处理

5. **Ping参数优化**：
   ```bash
   ping -c 3 -W 2 -i 0.2 {ip}
   # -c 3: 发送3个包（保证统计准确）
   # -W 2: 每个包最多等待2秒
   # -i 0.2: 包间隔0.2秒（加快速度）
   ```

6. **延迟分析算法**：
   - 正则提取`rtt min/avg/max/mdev`行
   - 解析为字典结构存储
   - 按最大延迟排序
   - 阈值判断（>1ms为高延迟）

7. **容错处理**：
   - Excel读取失败友好提示
   - SSH连接失败自动降级
   - Ping超时异常捕获
   - 空结果安全处理

```python
# 延迟分析示例
def analyze_ping_output(output):
    """
    分析ping输出，提取RTT信息
    """
    try:
        if not output or isinstance(output, str) and "失败" in output:
            return None
        
        # 查找rtt统计行
        for line in output.split('\n'):
            if 'rtt min/avg/max/mdev' in line:
                # 提取RTT值
                stats = line.split('=')[1].strip().split('/')
                return {
                    'min': float(stats[0]),
                    'avg': float(stats[1]),
                    'max': float(stats[2]),
                    'mdev': float(stats[3].split()[0])
                }
        return None
    except Exception:
        return None
```

### SSH连接池实现

为了实现真正的并发远程测试，实现了SSH连接池机制：

```python
class SSHConnectionPool:
    """SSH连接池，用于并发场景下管理多个SSH连接"""
    def __init__(self, hostname, username, password=None, key_file=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_file = key_file
    
    def create_connection(self):
        """创建一个新的SSH连接"""
        ssh = SSHClient(self.hostname, self.username, self.password, self.key_file)
        if ssh.connect():
            return ssh
        return None
    
    def execute_command_with_new_connection(self, command, timeout=30):
        """使用新连接执行命令，执行完成后关闭连接"""
        ssh = self.create_connection()
        if not ssh:
            return None
        try:
            result = ssh.execute_command(command, timeout)
            return result
        finally:
            ssh.close()  # 自动关闭连接
```

**关键优势**：
- 每个并发任务使用独立的SSH连接
- 避免了多线程共享单个SSH连接的竞争问题
- 自动管理连接生命周期，避免资源泄漏
- 支持高并发（20-30个线程）

## 系统要求

- Python 3.6+
- pandas（用于Excel文件处理）
- paramiko（用于SSH支持）

## 安装步骤

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows系统: .venv\Scripts\activate

# 安装依赖
pip install pandas paramiko
```

## 版本历史

历史版本保存在`his`目录中：
- 1.0.py: 初始版本
- 2.0.py: 功能改进版本
- 3.0.py: 进一步改进版本
- ping_v1.py: 基础版本，使用文本文件输入

当前版本:
- ping_v2.py: 最新版本，使用Excel输入并支持SSH

## 执行模式对比

| 特性 | 本地模式 | 远程模式 |
|-----|---------|---------|
| **触发条件** | Excel中无`server=1`的IP | Excel中有`server=1`的IP |
| **测试来源** | 运行脚本的机器 | 远程跳板机服务器 |
| **并发数** | 20（单个IP）/ 30（网段） | 5（单个IP）/ 5（网段） |
| **认证要求** | 无 | 需要SSH用户名和密码/密钥 |
| **网络要求** | 需要直接访问目标网络 | 通过跳板机访问隔离网络 |
| **性能** | 最优（无SSH开销） | 良好（受SSH连接限制） |
| **适用场景** | 同网段设备测试 | 跨网段、隔离网络测试 |
| **容错** | - | 连接失败自动降级为本地 |

### 自动模式切换

脚本会智能检测执行环境：
1. 如果Excel中存在`server=1`的IP → 尝试远程模式
2. 如果SSH连接失败 → 自动降级为本地模式
3. 如果Excel中无服务器配置 → 直接使用本地模式

## 使用场景

### 典型应用
- ✅ **网络管理员**：检查网络连通性，批量测试设备
- ✅ **系统管理员**：监控服务器可达性，健康检查
- ✅ **网络工程师**：网络故障排查，延迟分析
- ✅ **运维团队**：大规模设备批量测试，性能监控
- ✅ **数据中心**：跨网段连通性验证

### 实际场景示例

**场景1：数据中心网络验证**
- 从跳板机测试100台服务器连通性
- 自动识别高延迟节点
- 5分钟完成（传统方式需要1小时）

**场景2：办公网络健康检查**
- 本地测试所有网络设备
- 实时进度反馈
- 生成详细报告供分析

**场景3：跨网段隔离网络测试**
- 通过跳板机访问生产网络
- 避免直接暴露生产网络
- 安全且高效

## 性能优化说明

### v2.0 并发优化版本

本次更新重点优化了并发性能，主要改进包括：

1. **并发架构改进**：
   - 将单个IP处理改为批量并发模式
   - 使用`ThreadPoolExecutor`和`as_completed`实现真正的并发
   - 自动区分单个IP和网段，分别优化处理

2. **Ping参数优化**：
   - 从`-c 2 -W 5`优化为`-c 3 -W 2 -i 0.2`
   - 单个IP测试从~10秒降至~2秒
   - 包间隔从默认1秒降至0.2秒，提升5倍速度

3. **并发数量调整**：
   - 单个IP处理：20并发（适合少量IP快速测试）
   - 网段处理：30并发（适合大量IP批量测试）

4. **SSH连接池优化**（重要）：
   - **问题**：之前所有并发线程共享一个SSH连接，导致串行执行
   - **解决方案**：实现`SSHConnectionPool`，每个线程创建独立SSH连接
   - **效果**：远程测试实现真正的并发
   - **自动管理**：每次ping完成后自动关闭SSH连接，避免资源泄漏
   - **连接限制处理**：
     - SSH服务器通常有`MaxStartups`连接限制（默认10）
     - 远程测试并发数限制为5，避免超过服务器限制
     - 添加重试机制和递增延迟，提高连接成功率
     - 禁用详细日志输出，减少错误信息干扰

5. **性能提升**：
   - **本地测试**（并发20-30）：
     - 100个IP：从串行~1000秒降至并发~50秒（20倍提升）
     - 256个IP网段：从串行~2560秒降至并发~86秒（30倍提升）
   - **远程测试**（并发5，受SSH限制）：
     - 之前：SSH单连接导致实际串行执行
     - 现在：5个独立SSH连接并发
     - 100个IP：从串行~1000秒降至并发~200秒（5倍提升）
     - 受限于SSH服务器连接数，但仍有显著提升

## 故障排查

### SSH连接错误问题

**问题现象**：
```
Exception (client): Error reading SSH protocol banner
ConnectionResetError: [Errno 54] Connection reset by peer
```

**原因分析**：
1. SSH服务器有`MaxStartups`连接限制（通常默认10）
2. 并发连接数过多导致服务器拒绝新连接
3. 瞬间大量连接请求超过服务器处理能力

**解决方案**：
1. ✅ **已实现**：降低远程测试并发数为5
2. ✅ **已实现**：添加连接重试机制（最多重试2次）
3. ✅ **已实现**：添加递增延迟（0.5秒 × 重试次数）
4. ✅ **已实现**：禁用详细日志输出

**如需提高并发数**，在SSH服务器上调整配置：
```bash
# 编辑 /etc/ssh/sshd_config
MaxStartups 20:30:50  # 允许最多20个并发连接
MaxSessions 20         # 每个连接最多20个会话

# 重启SSH服务
systemctl restart sshd
```

### 性能调优建议

1. **本地测试**：无限制，建议使用20-30并发
2. **远程测试**：
   - 默认5并发（安全值）
   - 如调整了SSH服务器配置，可在代码中增加并发数
   - 修改位置：`ping_v2.py` 第144行和第450行

## 未来改进方向

- 添加Web界面，便于可视化结果
- 支持定时执行和历史数据比较
- 添加邮件或消息通知功能
- 扩展支持更多网络诊断工具（如traceroute）
- 改进数据可视化，添加图表展示
- 支持自定义并发数量和ping参数
- 支持配置文件管理并发数和超时参数