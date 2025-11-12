# 贡献指南

感谢你考虑为 Ping Tool 项目做出贡献！本文档提供了参与项目开发的指导方针。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试要求](#测试要求)
- [文档规范](#文档规范)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- ✅ 使用友好和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员保持同理心

### 不可接受的行为

- ❌ 使用性化的语言或图像
- ❌ 恶意评论、侮辱或人身攻击
- ❌ 公开或私下的骚扰
- ❌ 未经许可发布他人的私人信息
- ❌ 其他不道德或不专业的行为

---

## 如何贡献

### 🐛 报告Bug

发现Bug？请通过以下步骤报告：

1. **检查是否已存在**：查看 [Issues](https://github.com/yourorg/ping-tool/issues) 确认问题未被报告
2. **创建Issue**：使用Bug模板创建新Issue
3. **提供详细信息**：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（OS、Python版本等）
   - 错误日志或截图

### ✨ 提议新功能

想要新功能？欢迎提议：

1. **先讨论**：创建Feature Request Issue
2. **说明用途**：描述功能的使用场景
3. **考虑替代方案**：是否有其他实现方式
4. **等待反馈**：维护者会评估可行性

### 📖 改进文档

文档改进永远欢迎：

- 修正拼写错误
- 补充缺失的说明
- 添加使用示例
- 翻译文档

### 💻 贡献代码

遵循以下流程贡献代码：

1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

---

## 开发流程

### 1. 准备开发环境

```bash
# 1. Fork并克隆仓库
git clone https://github.com/your-username/ping-tool.git
cd ping-tool

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装开发依赖
make install-dev

# 4. 验证安装
python -c "from ping_tool import __version__; print(__version__)"
```

### 2. 创建功能分支

```bash
# 从main分支创建新分支
git checkout -b feature/your-feature-name

# 或修复bug
git checkout -b fix/bug-description
```

分支命名规范：
- `feature/功能名` - 新功能
- `fix/问题描述` - Bug修复
- `docs/说明` - 文档更新
- `refactor/说明` - 代码重构
- `test/说明` - 测试相关

### 3. 开发和测试

```bash
# 编写代码
vim src/ping_tool/...

# 运行测试
make test

# 代码检查
make lint

# 格式化代码
make format

# 查看覆盖率
open htmlcov/index.html
```

### 4. 提交变更

```bash
# 添加变更
git add .

# 提交（遵循提交规范）
git commit -m "feat: 添加新功能"

# 推送到远程
git push origin feature/your-feature-name
```

### 5. 创建Pull Request

1. 访问GitHub仓库
2. 点击 "New Pull Request"
3. 选择你的分支
4. 填写PR模板
5. 等待代码审查

---

## 代码规范

### Python风格指南

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# 好的示例
def calculate_latency(ip: str, timeout: int = 30) -> float:
    """
    计算网络延迟
    
    Args:
        ip: 目标IP地址
        timeout: 超时时间（秒）
        
    Returns:
        float: 延迟时间（毫秒）
    """
    pass

# 不好的示例
def calc(ip,t=30):
    pass
```

### 类型注解

**必须**使用类型注解：

```python
from typing import List, Dict, Optional

def ping_multiple(ips: List[str]) -> Dict[str, bool]:
    """Ping多个IP地址"""
    results: Dict[str, bool] = {}
    return results
```

### 文档字符串

使用Google风格文档字符串：

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """
    函数简短描述
    
    更详细的说明（可选）
    
    Args:
        arg1: 参数1说明
        arg2: 参数2说明，默认为0
        
    Returns:
        bool: 返回值说明
        
    Raises:
        ValueError: 异常说明
        
    Examples:
        >>> function("test", 10)
        True
    """
    pass
```

### 代码组织

```python
# 1. 标准库导入
import os
import sys

# 2. 第三方库导入
import pandas as pd
import paramiko

# 3. 本地导入
from .core import ping
from .utils import analysis
```

---

## 提交规范

### Commit Message格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建工具、依赖更新

### 示例

```bash
# 新功能
git commit -m "feat(ping): 添加IPv6支持"

# Bug修复
git commit -m "fix(ssh): 修复连接池内存泄漏问题"

# 文档更新
git commit -m "docs: 更新安装指南"

# 性能优化
git commit -m "perf(ping): 优化并发性能"

# 重大变更
git commit -m "feat!: 更改API接口

BREAKING CHANGE: ping_ip()函数签名已更改"
```

---

## 测试要求

### 单元测试

每个新功能**必须**包含测试：

```python
# tests/test_new_feature.py
import pytest
from ping_tool.new_feature import function

def test_function_success():
    """测试成功情况"""
    result = function("test")
    assert result is True

def test_function_failure():
    """测试失败情况"""
    with pytest.raises(ValueError):
        function(None)
```

### 测试覆盖率

- **最低要求**：新代码覆盖率 ≥ 80%
- **目标**：整体覆盖率 ≥ 85%

```bash
# 运行测试并查看覆盖率
make test

# 查看详细报告
open htmlcov/index.html
```

### 测试类型

1. **单元测试**：测试单个函数
2. **集成测试**：测试模块间交互
3. **功能测试**：测试完整功能

---

## 文档规范

### README更新

新功能需要更新README：

- 功能特点列表
- 使用示例
- 配置说明

### 代码注释

```python
# 好的注释：解释"为什么"
# 使用重试机制避免瞬时网络故障
retry_count = 3

# 不好的注释：解释"做什么"（代码已经说明）
# 设置重试次数为3
retry_count = 3
```

### CHANGELOG更新

在 `CHANGELOG.md` 的 `[Unreleased]` 部分添加变更。

---

## Pull Request检查清单

提交PR前，确保：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 代码覆盖率达标
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有合并冲突
- [ ] 通过了代码检查（lint）

---

## 代码审查

### 审查者职责

- ✅ 检查代码质量
- ✅ 验证功能正确性
- ✅ 确保测试充分
- ✅ 提供建设性反馈

### 贡献者职责

- ✅ 及时回复评论
- ✅ 修改代码问题
- ✅ 保持沟通友好

---

## 发布流程

（仅限维护者）

1. 更新版本号（`pyproject.toml`, `__init__.py`）
2. 更新 `CHANGELOG.md`
3. 创建Git标签
4. 构建发布包
5. 发布到PyPI

```bash
# 更新版本
vim pyproject.toml
vim src/ping_tool/__init__.py

# 更新CHANGELOG
vim CHANGELOG.md

# 提交并打标签
git commit -m "chore: bump version to 2.1.0"
git tag v2.1.0
git push origin main --tags

# 构建和发布
make build
python -m twine upload dist/*
```

---

## 获取帮助

需要帮助？可以：

- 💬 创建 [Discussion](https://github.com/yourorg/ping-tool/discussions)
- 📧 发送邮件到 network@example.com
- 📖 查看 [文档](README.md)

---

## 许可证

贡献代码即表示你同意代码将以 [MIT License](LICENSE) 发布。

---

## 致谢

感谢所有为项目做出贡献的人！

你的贡献让这个项目变得更好！🎉

