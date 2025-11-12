# 示例文件

本目录包含项目的示例配置文件，帮助快速上手使用。

## 文件说明

### credentials.example.xlsx
Excel凭证文件示例，包含以下列：

| 列名 | 说明 | 示例值 |
|-----|------|-------|
| IP | IP地址或网段 | `192.168.1.1` 或 `10.0.0.0/24` |
| user | SSH用户名 | `root` |
| pass | SSH密码 | `mypassword` |
| server | 是否为跳板机 | `1`（是）或 `0`（否）|

## 使用方法

### 1. 复制示例文件

```bash
# 复制到实际使用的位置
cp examples/credentials.example.xlsx pass/credentials.xlsx

# 编辑填写真实的凭证信息
```

### 2. 配置说明

#### 跳板机服务器配置
设置 `server=1` 的行将被识别为跳板机：

```
IP              user    pass        server
10.201.96.12    root    mypass123   1        # 跳板机
```

#### 目标IP配置
设置 `server=0` 的行为测试目标：

```
IP              user    pass        server
192.168.1.1     -       -           0        # 目标IP
192.168.1.2     -       -           0        # 目标IP
```

#### 网段配置
支持CIDR表示法：

```
IP              user    pass        server
10.0.0.0/24     -       -           0        # 整个网段
192.168.1.0/24  -       -           0        # 192.168.1.1-254
```

### 3. 认证方式

#### 密码认证
```
IP              user    pass        server
10.201.96.12    root    123456      1
```

#### 密钥认证
留空密码，将密钥文件放到 `pass/key/{username}`：

```
IP              user    pass        server
10.201.96.12    admin   -           1
```

密钥文件位置：`pass/key/admin`

### 4. 安全建议

⚠️ **重要**：
- ❌ 不要将包含真实密码的文件提交到Git
- ✅ 使用 `.gitignore` 忽略 `pass/credentials.xlsx`
- ✅ 优先使用SSH密钥认证
- ✅ 敏感文件设置适当的权限 `chmod 600`

## 完整示例

### 场景1：本地测试
不需要跳板机，直接测试网络设备：

```
IP              user    pass    server
192.168.1.1     -       -       0
192.168.1.2     -       -       0
192.168.1.254   -       -       0
```

### 场景2：通过跳板机测试
从跳板机访问隔离网络：

```
IP              user    pass        server
10.201.96.12    root    mypass      1        # 跳板机
192.168.1.1     -       -           0        # 目标1
192.168.1.2     -       -           0        # 目标2
10.0.0.0/24     -       -           0        # 目标网段
```

### 场景3：混合网段测试
单个IP和网段混合：

```
IP              user    pass        server
10.201.96.12    admin   -           1        # 跳板机（密钥认证）
10.201.96.1     -       -           0        # 单个IP
10.201.96.2     -       -           0        # 单个IP
10.201.98.0/24  -       -           0        # 整个网段
10.201.109.0/24 -       -           0        # 整个网段
```

## 故障排查

### 问题1：Excel读取失败
```
错误：读取 Excel 文件失败
```
**解决**：
- 确保文件格式正确（.xlsx）
- 检查文件权限
- 确认pandas和openpyxl已安装

### 问题2：SSH连接失败
```
错误：连接失败 10.201.96.12: Error reading SSH protocol banner
```
**解决**：
- 检查网络连通性：`ping 10.201.96.12`
- 确认SSH服务运行：`telnet 10.201.96.12 22`
- 验证用户名密码正确
- 检查SSH服务MaxStartups限制

### 问题3：密钥认证失败
```
错误：No such file or directory: 'pass/key/admin'
```
**解决**：
- 确保密钥文件存在
- 检查文件权限：`chmod 600 pass/key/admin`
- 验证密钥格式正确（RSA/Ed25519）

## 更多帮助

查看完整文档：
- [README.md](../README.md) - 项目总览
- [docs/INSTALL.md](../docs/INSTALL.md) - 安装指南
- [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) - 开发指南

