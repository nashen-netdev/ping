# 从服务器 Ping 功能说明

## 概述

在 ping-ip-planning 工具中，针对 **server&security** sheet 页新增了"从服务器ping"功能。此功能允许用户指定一台服务器，脚本将自动：

1. 在 Excel 中查找该服务器的登录凭据（System User 和 System Password）
2. 使用这些凭据通过 SSH 登录到该服务器
3. 从该服务器执行 ping 测试，测试其他目标设备的连通性

## 使用场景

此功能特别适用于以下场景：

- **网络隔离环境**：目标设备只能从特定服务器访问
- **跳板机测试**：需要从跳板机测试内网设备
- **服务器视角测试**：验证从服务器角度的网络连通性
- **分布式网络测试**：从不同服务器测试网络质量

## 前提条件

### Excel 文件要求

server&security sheet 必须包含以下列：

| 列名 | 说明 | 示例 |
|-----|------|------|
| `hostname` | 服务器主机名 | `web-server-01` |
| `管理网地址` 或 `MGMT` | 服务器管理网IP | `192.168.1.100` |
| `System User` | SSH 登录用户名 | `root` 或 `admin` |
| `System Password` | SSH 登录密码 | `password123` |

### 网络要求

- 运行脚本的机器能够 SSH 访问目标服务器
- 目标服务器能够访问其他需要测试的设备

## 使用方法

### 交互式模式（推荐）

```bash
ping-ip-planning
```

交互流程：

```
1. 选择环境（如：金茂）
   ✓ 已选择环境: 金茂
   文件: pass/IP地址规划表-金茂1.xlsx

2. 选择 Sheet 页
   请选择 Sheet（必选，输入 q 退出）: 2
   ✓ 已选择: server&security

3. 选择要 ping 的列
   请选择列（输入 q 退出）: 1
   ✓ 已选择: 管理网地址

4. 选择 Ping 模式  【🆕 新增】
   请选择 Ping 模式（输入 q 退出）[1]: 2
   ✓ 已选择: 从服务器 ping
   
   服务器标识（hostname或IP）: web-server-01
   ✓ 将从服务器 'web-server-01' ping 其他设备

5. 颜色过滤设置
   是否只 ping 绿色单元格？(y/n) [n]: n
   ✓ 不过滤颜色，ping 所有设备
```

### 命令行模式

虽然新功能主要针对交互式模式，但也可以通过配置文件使用：

```yaml
# env/my_env.yaml
name: "测试环境"
file: "pass/IP地址规划表.xlsx"
sheet: "server&security"
column: "管理网地址"
use_remote_server: true
server_identifier: "web-server-01"  # hostname 或 IP
```

然后运行：

```bash
# 运行后选择对应的环境
ping-ip-planning
```

## 工作流程

### 1. 查找服务器凭据

脚本在 Excel 的 server&security sheet 中查找匹配的服务器：

- 支持通过 **hostname** 查找
- 支持通过 **管理网IP地址** 查找
- 查找时不区分大小写

示例输出：

```
======================================================================
正在查找服务器凭据...
======================================================================
正在读取 pass/IP地址规划表-金茂1.xlsx 的 server&security sheet...
找到表头行: 第1行
  hostname 列索引: 0
  管理网IP 列索引: 3
  System User 列索引: 10
  System Password 列索引: 11
开始查找服务器: web-server-01
✓ 找到服务器: web-server-01 (192.168.1.100)

服务器信息:
  主机名: web-server-01
  管理网IP: 192.168.1.100
  用户名: root
======================================================================
```

### 2. 建立 SSH 连接

脚本使用找到的凭据测试 SSH 连接：

```
正在测试服务器连接...
✓ 成功连接到服务器 web-server-01 (192.168.1.100)
```

### 3. 执行 Ping 测试

从该服务器并发 ping 其他设备：

```
找到 50 个 IP 地址:
  - 192.168.1.10    (app-server-01)
  - 192.168.1.11    (app-server-02)
  ... 还有 48 个

测试来源: 192.168.1.100 (远程)
并发数: 5

开始 ping 测试...
------------------------------------------------------------
✓ 192.168.1.10    (app-server-01              ) - 可达
✓ 192.168.1.11    (app-server-02              ) - 可达
✗ 192.168.1.12    (app-server-03              ) - 不可达
  进度: 3/50 (6.0%)
...
```

### 4. 生成测试报告

测试完成后生成详细报告：

```
============================================================
测试结果统计
============================================================
总计 IP 数量: 50
可达 IP 数量: 48
不可达 IP 数量: 2
可达率: 96.0%
============================================================

详细结果已写入: logs/ping_results_server_security.log
```

## 错误处理

### 服务器未找到

```
✗ 未找到匹配的服务器: web-server-01
将使用本地 ping
```

**解决方法**：
- 检查输入的 hostname 或 IP 是否正确
- 确认 Excel 文件中存在该服务器记录
- 检查 hostname 列和管理网地址列的数据

### 凭据缺失

```
✗ 找到服务器 web-server-01，但 System User 为空
```

或

```
✗ 找到服务器 web-server-01，但 System Password 为空
```

**解决方法**：
- 在 Excel 中填写该服务器的 System User 和 System Password
- 确保这两列不为空

### SSH 连接失败

```
✗ 无法连接到服务器 web-server-01 (192.168.1.100)，将使用本地 ping
```

**可能原因**：
1. 网络不可达
2. SSH 服务未启动
3. 用户名或密码错误
4. 防火墙阻止连接
5. SSH 端口不是默认的 22

**解决方法**：
- 手动测试 SSH 连接：`ssh user@192.168.1.100`
- 检查服务器是否在线：`ping 192.168.1.100`
- 确认用户名和密码正确
- 检查防火墙规则

## 与原有功能的区别

### 原有远程 ping

- 从 `credentials.xlsx` 中查找标记为 `server=1` 的跳板机
- 自动选择第一个可用的服务器
- 适用于标准 ping 工具

### 新增从服务器 ping

- **仅限 server&security sheet**
- **用户指定具体的服务器**（hostname 或 IP）
- 从 Excel 同一个文件中读取服务器凭据
- 灵活选择测试源服务器
- 适用于 IP 地址规划表场景

## 示例场景

### 场景 1：测试应用服务器连通性

某数据中心有多台应用服务器，需要从 web 前端服务器测试到后端数据库的连通性。

```bash
ping-ip-planning
# 选择 server&security
# 选择 "从服务器 ping"
# 输入: web-server-01
```

结果：从 web-server-01 测试所有数据库服务器的连通性。

### 场景 2：跳板机隔离网络测试

生产环境通过跳板机访问，需要验证跳板机到生产服务器的网络。

```bash
ping-ip-planning
# 选择 server&security
# 选择 "从服务器 ping"
# 输入: jumpserver-prod
```

结果：从跳板机测试所有生产服务器的可达性。

### 场景 3：多数据中心网络质量对比

对比从不同数据中心服务器到同一目标的网络质量。

**测试 1：从北京机房**
```bash
ping-ip-planning
# 输入: bj-server-01
```

**测试 2：从上海机房**
```bash
ping-ip-planning
# 输入: sh-server-01
```

对比两次测试的延迟和可达率。

## 最佳实践

1. **使用 hostname 优先**：比 IP 更易读，便于管理
2. **测试前验证凭据**：确保 Excel 中的用户名密码正确
3. **网络规划**：确保测试源服务器能访问目标设备
4. **并发控制**：大量设备测试时，注意 SSH 连接数限制（默认并发 5）
5. **日志分析**：测试完成后查看日志文件，分析详细结果

## 技术实现

### 关键函数

**excel_reader.py**：

```python
def find_server_credentials(file_path, sheet_name, identifier):
    """
    根据 hostname 或 IP 查找服务器凭据
    返回：{hostname, mgmt_ip, username, password, row}
    """
```

**config_manager.py**：

```python
def interactive_select_ping_mode(sheet_name):
    """
    交互式选择 ping 模式
    返回：{use_remote_server, server_identifier}
    """
```

**cli_ip_planning.py**：

```python
# 查找服务器凭据
server_creds = find_server_credentials(file_path, sheet_name, server_identifier)

# 创建 SSH 连接池
server_ssh_pool = SSHConnectionPool(server_ip, username, password)

# 使用该服务器执行 ping
ping_ip_remote(server_ssh_pool, target_ip)
```

## 常见问题（FAQ）

**Q: 此功能只能用于 server&security sheet 吗？**

A: 是的。network&security sheet 通常用于网络设备，没有 System User/Password 列，因此不支持此功能。

**Q: 可以同时测试多个源服务器吗？**

A: 当前版本每次只能选择一个源服务器。如需从多个服务器测试，请分别运行多次。

**Q: 为什么不直接使用 --local 参数？**

A: --local 是从运行脚本的机器 ping。而"从服务器 ping"是登录到指定的远程服务器后 ping，两者测试源不同。

**Q: 支持 SSH 密钥认证吗？**

A: 当前版本仅支持密码认证。密钥认证功能计划在后续版本中添加。

**Q: 如果服务器连接失败会怎样？**

A: 脚本会自动降级为本地 ping，不会中断测试。

## 版本历史

- **v2.1.0** (2026-01-12): 新增从服务器 ping 功能
  - 支持指定服务器作为测试源
  - 自动从 Excel 读取服务器凭据
  - 交互式选择 ping 模式

## 相关文档

- [IP 地址规划表使用指南](IP_PLANNING_USAGE.md)
- [交互式流程说明](INTERACTIVE_FLOW.md)
- [环境配置管理](../env/README.md)
