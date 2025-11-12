# 测试文档

## 📊 测试覆盖率现状

截至最新版本，项目测试覆盖率情况：

| 模块 | 覆盖率 | 说明 |
|------|--------|------|
| `core/ping.py` | 86% | Ping核心功能 |
| `core/ssh.py` | 92% | SSH连接管理 |
| `utils/credentials.py` | 100% | 凭证管理 ✅ |
| `utils/analysis.py` | 82% | 延迟分析 |
| `utils/network.py` | 80% | 网络工具 |
| `__init__.py` | 100% | 包初始化 ✅ |
| **总体** | **86%** | **已达标！** ✅ |

> 🎯 **目标达成**：核心模块覆盖率已超过80%，CLI模块暂不计入（交互性强，难以单元测试）

## 📝 测试文件清单

```
tests/
├── __init__.py
├── test_analysis.py      # 延迟分析测试（4个测试用例）
├── test_credentials.py   # 凭证管理测试（6个测试用例）
├── test_network.py       # 网络工具测试（1个测试用例）
├── test_ping.py          # Ping功能测试（8个测试用例）
└── test_ssh.py           # SSH连接测试（10个测试用例）
```

**总计**：5个测试文件，29个测试用例，全部通过 ✅

## 🧪 测试用例详情

### 1. test_ping.py - Ping功能测试

#### 本地Ping测试
- ✅ `test_ping_ip_local_success` - 测试本地ping成功
- ✅ `test_ping_ip_local_failure` - 测试本地ping失败
- ✅ `test_ping_ip_local_timeout` - 测试本地ping超时

#### 远程Ping测试
- ✅ `test_ping_ip_remote_success` - 测试远程ping成功
- ✅ `test_ping_ip_remote_failure` - 测试远程ping失败
- ✅ `test_ping_ip_remote_connection_fail` - 测试SSH连接失败

#### 网段Ping测试
- ✅ `test_ping_network_local` - 测试本地网段扫描

### 2. test_ssh.py - SSH连接测试

#### SSHClient测试
- ✅ `test_connect_with_password_success` - 密码认证成功
- ✅ `test_connect_with_password_failure` - 密码认证失败
- ✅ `test_connect_with_key` - 密钥认证
- ✅ `test_execute_command_success` - 命令执行成功
- ✅ `test_execute_command_no_client` - 未连接时执行命令
- ✅ `test_close` - 关闭连接

#### SSHConnectionPool测试
- ✅ `test_create_connection_success` - 创建连接成功
- ✅ `test_create_connection_with_retry` - 连接重试机制
- ✅ `test_create_connection_max_retries_exceeded` - 超过最大重试次数
- ✅ `test_execute_command_with_new_connection` - 使用新连接执行命令
- ✅ `test_execute_command_connection_fail` - 连接失败时执行命令

### 3. test_credentials.py - 凭证管理测试

- ✅ `test_get_credentials_success` - 成功获取凭证
- ✅ `test_get_credentials_with_integer_password` - 处理整数密码
- ✅ `test_get_credentials_with_null_password` - 处理空密码
- ✅ `test_get_credentials_no_server_column` - 处理缺失server列
- ✅ `test_get_credentials_ip_not_found` - IP不存在的情况
- ✅ `test_get_credentials_file_not_found` - 文件不存在的情况

### 4. test_analysis.py - 延迟分析测试

- ✅ `test_analyze_ping_output_success` - 成功解析延迟
- ✅ `test_analyze_ping_output_failure` - 处理失败的ping
- ✅ `test_analyze_ping_output_empty` - 处理空输出
- ✅ `test_analyze_ping_output_none` - 处理None输出

### 5. test_network.py - 网络工具测试

- ✅ `test_get_local_ip` - 获取本地IP地址

## 🚀 运行测试

### 运行所有测试

```bash
# 使用Makefile（推荐）
make test

# 或直接使用pytest
python3 -m pytest tests/ -v
```

### 查看覆盖率报告

```bash
# 生成覆盖率报告
make test

# 打开HTML报告
open htmlcov/index.html
```

### 运行特定测试文件

```bash
# 只测试SSH功能
python3 -m pytest tests/test_ssh.py -v

# 只测试凭证管理
python3 -m pytest tests/test_credentials.py -v
```

### 运行特定测试用例

```bash
# 运行单个测试用例
python3 -m pytest tests/test_ping.py::TestPingLocal::test_ping_ip_local_success -v
```

## 📈 未来测试计划

### 短期目标（v2.1.0）
- [ ] 添加CLI模块集成测试
- [ ] 添加网段扫描边界测试
- [ ] 添加性能基准测试
- [ ] 增加异常场景测试

### 中期目标（v2.2.0）
- [ ] 实现端到端测试
- [ ] 添加压力测试
- [ ] 实现测试数据工厂
- [ ] 配置测试CI/CD

### 长期目标（v3.0.0）
- [ ] 实现模糊测试（fuzzing）
- [ ] 添加安全测试
- [ ] 实现性能回归测试
- [ ] 测试覆盖率达到95%+

## 🔧 测试最佳实践

### 1. 使用Mock隔离外部依赖

```python
from unittest.mock import Mock, patch

@patch('ping_tool.core.ssh.paramiko.SSHClient')
def test_connect(mock_ssh):
    # 模拟SSH连接，不依赖真实服务器
    pass
```

### 2. 测试边界条件

```python
def test_ping_invalid_ip():
    """测试无效IP地址"""
    result = ping_ip_local("999.999.999.999")
    assert result[1] is False
```

### 3. 测试异常处理

```python
def test_connection_timeout():
    """测试连接超时"""
    with pytest.raises(TimeoutError):
        ssh_client.connect(timeout=0.001)
```

### 4. 使用Fixture共享测试数据

```python
@pytest.fixture
def sample_credentials():
    """提供示例凭证数据"""
    return {
        'username': 'root',
        'password': 'test123',
        'is_server': True
    }

def test_with_fixture(sample_credentials):
    assert sample_credentials['username'] == 'root'
```

## 📊 持续集成

### GitHub Actions配置（规划中）

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: make install-dev
      - name: Run tests
        run: make test
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 🐛 调试测试

### 详细输出模式

```bash
# 显示print输出
python3 -m pytest tests/ -v -s

# 显示失败的详细信息
python3 -m pytest tests/ -v --tb=long

# 只运行失败的测试
python3 -m pytest tests/ --lf
```

### 使用pdb调试

```python
def test_something():
    result = function()
    import pdb; pdb.set_trace()  # 在此设置断点
    assert result is True
```

## 📚 相关文档

- [开发指南](DEVELOPMENT.md)
- [贡献指南](../CONTRIBUTING.md)
- [项目架构](../ARCHITECTURE.md)

---

**最后更新**：2025-11-12  
**测试框架**：pytest 9.0.0  
**覆盖率工具**：coverage 7.11.3

