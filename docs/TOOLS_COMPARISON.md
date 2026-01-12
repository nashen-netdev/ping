# Ping 工具对比与职责划分

本文档说明项目中三个 ping 工具的职责划分和使用场景。

## 📦 工具概览

项目包含 **3 个 ping 相关工具**，各自有明确的职责定位：

### 1. **标准 Ping 工具** (`cli.py`)
**命令**: `ping-tool`

**职责定位**: 
- ✅ **专用于 credentials.xlsx 文件**
- ✅ 标准化的凭证管理和批量测试

**功能特点**:
- 从 `credentials.xlsx` 读取 IP 和凭证
- 支持单个 IP 或 CIDR 网段测试
- **自动识别跳板机**（server=1）
- 支持本地/远程 SSH 并发测试
- 完整的延迟质量分析
- 日志输出: `logs/ping_results.log`

**使用场景**: 
- 批量测试设备连通性（使用 credentials.xlsx）
- 从跳板机测试隔离网络
- 网络质量监控
- 需要统一管理多个环境的凭证

**示例**:
```bash
ping-tool
# 自动读取 credentials.xlsx
# 自动识别 server=1 的跳板机
# 从跳板机 ping 所有目标 IP
```

---

### 2. **IP 地址规划表 Ping 工具** (`cli_ip_planning.py`)
**命令**: `ping-ip-planning`

**职责定位**: 
- ✅ **专用于 IP 地址规划表 Excel 文件**
- ✅ 不依赖 credentials.xlsx，所有信息来自规划表

**功能特点**:
- 从 IP 地址规划表 Excel 读取数据
- 支持 `network&security` 和 `server&security` sheet
- 三步式交互流程（环境→Sheet→模式）
- 支持颜色过滤（绿色单元格）
- 自动排除删除线的 IP
- **从服务器 ping**: 从 Excel 中读取服务器凭据（System User/Password）
- 完整的延迟质量分析
- 日志输出: `logs/ping_results_{sheet_name}.log`

**使用场景**:
- IP 地址规划表设备测试
- 项目环境管理（金茂、北京08等）
- 从特定服务器测试网络（凭据来自 Excel）
- 网络设备和服务器连通性验证
- 独立的测试环境，不需要额外的 credentials.xlsx

**示例**:
```bash
ping-ip-planning
# 1. 选择环境（如：金茂）
# 2. 选择 Sheet: server&security
# 3. 选择 Ping 模式: 从服务器 ping
# 4. 输入服务器标识: web-server-01
# 5. 自动从 Excel 读取 System User/Password
```

---

### 3. **环境配置管理工具** (`cli_env_add.py`)
**命令**: `ping-env-add`

**职责定位**: 
- ✅ **快速创建环境配置文件**

**功能特点**:
- 快速创建环境配置文件
- 自动生成 YAML 格式配置
- 支持自定义显示名称
- 配置文件存储在 `env/` 目录

**使用场景**:
- 快速添加新项目环境
- 简化配置管理

**示例**:
```bash
ping-env-add bj08 /path/to/IP规划表.xlsx --display-name "北京08机房"
```

---

## 📊 详细对比表

| 特性 | ping-tool | ping-ip-planning | ping-env-add |
|------|-----------|------------------|--------------|
| **类型** | Ping 测试工具 | IP 规划表专用工具 | 配置管理工具 |
| **数据源** | credentials.xlsx | IP地址规划表.xlsx | 无（创建配置） |
| **凭据来源** | credentials.xlsx (server=1) | Excel 内置 (System User/Password) | - |
| **支持 Sheet** | 单个 | 多个（net&sec/server&security） | - |
| **跳板机识别** | ✅ 自动识别 (server=1) | ❌ 不依赖 credentials.xlsx | - |
| **从服务器 ping** | ❌ | ✅ 从 Excel 读取凭据 | - |
| **交互流程** | 简单 | 三步式（环境→Sheet→模式） | 命令行参数 |
| **延迟分析** | ✅ | ✅ | - |
| **颜色过滤** | ❌ | ✅ | - |
| **删除线过滤** | ❌ | ✅ | - |
| **环境管理** | ❌ | ✅ | ✅ |
| **CIDR 网段** | ✅ | ❌ | - |
| **职责定位** | credentials.xlsx 专用 | IP 规划表专用 | 环境配置 |
| **依赖文件** | 必须有 credentials.xlsx | 只需 IP 规划表 | - |

---

## 🎯 职责划分说明

### 为什么要明确划分职责？

**v2.3.0 之前的问题**：
- ❌ `cli_ip_planning.py` 同时支持两种远程 SSH 方式：
  1. 从 Excel 读取服务器凭据（新功能）
  2. 从 credentials.xlsx 读取跳板机（旧逻辑）
- ❌ 导致功能重复，用户困惑
- ❌ 职责不清晰

**v2.3.0 的改进**：
- ✅ **明确职责**：每个工具有独特的职责
- ✅ **删除重复**：移除 `cli_ip_planning.py` 中的 credentials.xlsx 逻辑
- ✅ **用户清晰**：用户根据文件类型选择工具

### 职责划分原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 每个工具专注一种数据源 |
| **功能互补** | 工具之间功能互补，不重复 |
| **独立运行** | 每个工具可独立运行，不强制依赖其他文件 |
| **清晰定位** | 用户一眼就能看出该用哪个工具 |

---

## 💡 使用决策树

```
需要 ping 测试
  │
  ├─ 使用 credentials.xlsx 管理凭证？
  │   └─ YES → 使用 ping-tool
  │        - 自动识别跳板机
  │        - 支持 CIDR 网段
  │
  └─ 使用 IP 地址规划表？
      └─ YES → 使用 ping-ip-planning
           │
           ├─ 需要从本地 ping？
           │   └─ 选择 "从本地 ping"
           │
           └─ 需要从某台服务器 ping？
               └─ 选择 "从服务器 ping"
                  └─ 输入服务器 hostname/IP
                  └─ 自动从 Excel 读取凭据
```

---

## 🔄 版本历史

### v2.3.0 (2026-01-12)
- ✅ 明确职责划分
- ✅ 删除 `cli_ip_planning.py` 中的 credentials.xlsx 逻辑
- ✅ 新增"从服务器 ping"功能（使用 Excel 凭据）
- ✅ 新增延迟质量分析

### v2.2.0 (2026-01-11)
- 环境配置管理改进

### v2.1.0 (2026-01-10)
- 新增 IP 地址规划表 Ping 工具

---

## 📝 最佳实践

### 1. 选择正确的工具

**使用 ping-tool 当**:
- ✅ 你有标准的 credentials.xlsx 文件
- ✅ 需要测试多个环境的设备
- ✅ 使用统一的跳板机管理
- ✅ 需要测试 CIDR 网段

**使用 ping-ip-planning 当**:
- ✅ 你有 IP 地址规划表
- ✅ 需要按颜色过滤测试对象
- ✅ 需要从特定服务器测试
- ✅ 测试目标和凭据在同一个文件中
- ✅ 不想维护额外的 credentials.xlsx

### 2. 文件组织建议

```
project/
├── pass/
│   ├── credentials.xlsx          # 用于 ping-tool
│   ├── IP地址规划表-金茂.xlsx    # 用于 ping-ip-planning
│   └── IP地址规划表-bj08.xlsx   # 用于 ping-ip-planning
│
├── env/
│   ├── jinmao.yaml                # 金茂环境配置
│   └── bj08.yaml                  # 北京08环境配置
│
└── logs/
    ├── ping_results.log           # ping-tool 输出
    ├── ping_results_net_sec.log   # ping-ip-planning 输出
    └── ping_results_server_security.log
```

### 3. 常见场景示例

#### 场景 1：使用跳板机测试多个 IP
```bash
# 准备 credentials.xlsx
# IP列: 10.0.0.1, 10.0.0.2, 192.168.1.0/24
# server列: 1, 0, 0

ping-tool
# 自动从 10.0.0.1 跳板机测试其他 IP
```

#### 场景 2：测试 IP 规划表中的网络设备
```bash
ping-ip-planning
# 选择: network&security
# 从本地 ping 所有设备
```

#### 场景 3：从指定服务器测试其他服务器
```bash
ping-ip-planning
# 选择: server&security
# 选择: 从服务器 ping
# 输入: jumpserver-01
# 从 jumpserver-01 测试所有其他服务器
```

---

## ❓ FAQ

**Q: 为什么不把两个工具合并成一个？**

A: 职责明确，各司其职。合并会导致：
- 参数复杂，用户困惑
- 代码维护困难
- 功能耦合，难以扩展

**Q: 如果我既有 credentials.xlsx 又有 IP 规划表怎么办？**

A: 根据测试需求选择：
- 测试 credentials.xlsx 中的设备 → 用 `ping-tool`
- 测试 IP 规划表中的设备 → 用 `ping-ip-planning`

**Q: 可以在 ping-ip-planning 中使用 credentials.xlsx 的跳板机吗？**

A: 不能（v2.3.0 已移除此功能）。理由：
- 避免功能重复
- 保持工具职责清晰
- IP 规划表应该自包含所有信息

**Q: 如何快速添加新的测试环境？**

A: 使用 `ping-env-add` 命令：
```bash
ping-env-add new_env /path/to/规划表.xlsx --display-name "新环境"
```

---

## 🔗 相关文档

- [README.md](../README.md) - 项目主文档
- [从服务器 Ping 功能说明](SERVER_PING_MODE.md)
- [IP 地址规划表使用指南](IP_PLANNING_USAGE.md)
- [环境配置管理](../env/README.md)
- [CHANGELOG.md](../CHANGELOG.md) - 版本历史
