# 网络 Ping 测试工具

一个全面的网络连通性测试工具，用于测试多个IP地址或IP网段的连通性并测量延迟。

## 功能特点

- 支持单个IP地址或整个网段的Ping测试
- 可以在本地或通过远程服务器运行测试
- **高性能并发执行**：
  - 单个IP测试：支持最多20个并发线程
  - 网段测试：支持最多30个并发线程
  - 优化的ping参数（3个包，0.2秒间隔），快速完成测试
- 详细的测试结果记录，包括：
  - 可达/不可达的IP地址列表
  - 延迟统计数据（最小值/平均值/最大值/抖动）
  - 识别高延迟连接（>1ms）
  - 实时进度显示（带成功/失败标记）
- 支持SSH连接远程服务器进行测试

## 项目结构

```
.
├── address/            # 包含IP地址列表的目录
│   └── ip.txt          # 示例IP地址列表
├── his/                # 历史版本目录
│   ├── 1.0.py          # 早期版本
│   ├── 2.0.py          # 早期版本
│   ├── 3.0.py          # 早期版本
│   └── ping_v1.py      # 早期版本
├── log/                # 存储Ping测试结果的目录
│   └── ping_results.log # 测试结果日志
├── pass/               # 凭证目录
│   ├── credentials.xlsx # 用于SSH访问的服务器凭证
│   └── key/            # SSH密钥文件
├── ping_v2.py          # 主程序（从Excel读取IP，支持SSH）
└── README.md           # 本文件
```

## 使用方法

从Excel文件读取IP地址和凭证，可以从本地或远程服务器执行Ping测试。

```bash
python ping_v2.py
```

## 输入格式

创建Excel文件`pass/credentials.xlsx`，包含以下列：
- `IP`：要Ping的IP地址或服务器IP
- `user`：SSH访问的用户名
- `pass`：SSH访问的密码
- `server`：服务器IP设置为1，目标IP设置为0

## 输出格式

工具在`log`目录中生成详细的日志文件，包含：
- 汇总统计信息（总IP数，可达/不可达数量）
- 高延迟连接的延迟分析
- 每个IP地址的详细Ping结果

## 技术实现分析

本工具实现了以下功能：
1. 从Excel文件读取IP和凭证信息
2. 支持通过SSH连接远程服务器执行ping测试
3. 使用Python的`subprocess`模块执行系统ping命令
4. **高性能并发处理**：
   - 通过`ThreadPoolExecutor`并行处理多个IP地址
   - 单个IP：20线程并发（本地/远程）
   - 网段IP：30线程并发（本地/远程）
   - 优化的ping参数（`-c 3 -W 2 -i 0.2`），大幅提升测试速度
5. 智能分类处理：自动区分单个IP和网段，分别并发处理
6. 详细的延迟分析，包括最小/平均/最大/抖动值
7. 识别高延迟连接（>1ms）
8. 实时进度反馈，显示成功/失败状态
9. 生成全面的日志记录

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

## 使用场景

- 网络管理员检查网络连通性
- 系统管理员监控服务器可达性
- 网络故障排查
- 网络性能分析和延迟测量
- 大规模网络设备批量测试

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