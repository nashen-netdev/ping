# 项目架构说明

## 项目重构概述

本项目已从原始的单文件脚本重构为专业的Python项目架构，符合Python社区最佳实践。

## 架构决策

### 1. Src-Layout 结构

采用 **src-layout** 而非 flat-layout 的原因：

**优势**：
- ✅ 避免包导入混淆（开发时不会误导入根目录的包）
- ✅ 强制通过安装测试（确保打包正确）
- ✅ 更清晰的项目结构
- ✅ 符合现代Python项目标准

**目录对比**：
```python
# Flat Layout（不推荐）
ping_tool/
    __init__.py
    cli.py

# Src Layout（推荐）
src/
    ping_tool/
        __init__.py
        cli.py
```

### 2. 模块化设计

#### 分层架构

```
┌─────────────────────────┐
│   CLI Layer (cli.py)    │  ← 用户交互层
├─────────────────────────┤
│   Core Layer            │  ← 核心业务逻辑
│   - ping.py             │
│   - ssh.py              │
├─────────────────────────┤
│   Utils Layer           │  ← 工具函数
│   - analysis.py         │
│   - credentials.py      │
│   - network.py          │
└─────────────────────────┘
```

#### 职责分离

- **core/**: 核心功能，不依赖外部输入
- **utils/**: 可复用工具函数
- **models/**: 数据模型（预留扩展）
- **cli.py**: 命令行接口，整合所有功能

### 3. 依赖管理

#### pyproject.toml (PEP 621)

现代Python项目标准，替代传统的 setup.py：

**优势**：
- ✅ 声明式配置
- ✅ 工具统一（setuptools, pip, build）
- ✅ 元数据完整
- ✅ 开发/生产依赖分离

#### requirements.txt

保留兼容性，便于快速安装。

### 4. 包管理

#### 安装方式

```bash
# 开发模式（推荐）
pip install -e .

# 构建安装
pip install .

# 直接从whl安装
pip install dist/ping_tool-*.whl
```

#### 运行方式

```python
# 作为模块
python -m ping_tool

# 作为命令（需安装）
ping-tool

# 兼容脚本
python ping.py
```

### 5. 测试框架

#### pytest 配置

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src/ping_tool"
```

#### 测试结构

```
tests/
├── test_analysis.py      # 延迟分析测试
├── test_network.py       # 网络工具测试
├── test_ping.py          # Ping功能测试（待添加）
└── test_ssh.py           # SSH连接测试（待添加）
```

### 6. 配置管理

#### 多层配置

1. **defaults**: 代码中的默认值
2. **config.yaml**: 用户配置文件
3. **environment**: 环境变量（预留）

#### 配置优先级

```
环境变量 > config.yaml > 代码默认值
```

## 代码规范

### 类型注解

```python
def ping_ip_local(ip: str) -> tuple[str, bool, str]:
    """
    函数必须包含类型注解和文档字符串
    """
    pass
```

### 文档字符串

采用 Google Style：

```python
def function(arg1: str, arg2: int) -> bool:
    """
    简短描述
    
    详细说明（可选）
    
    Args:
        arg1: 参数1说明
        arg2: 参数2说明
        
    Returns:
        bool: 返回值说明
        
    Raises:
        ValueError: 异常说明
    """
    pass
```

### 代码风格

- **black**: 代码格式化
- **isort**: import排序
- **flake8**: 代码检查
- **mypy**: 类型检查

## 开发工作流

### 1. 环境设置

```bash
python -m venv .venv
source .venv/bin/activate
make install-dev
```

### 2. 开发迭代

```bash
# 编写代码
vim src/ping_tool/...

# 运行测试
make test

# 代码检查
make lint

# 格式化
make format
```

### 3. 提交代码

```bash
git add .
git commit -m "feat: 新功能"
```

## 扩展指南

### 添加新功能模块

1. 在适当目录创建新文件
2. 编写对应测试
3. 更新 `__init__.py` 导出
4. 更新文档

### 添加新依赖

```bash
# 编辑 pyproject.toml
[project]
dependencies = [
    "new-package>=1.0.0",
]

# 重新安装
pip install -e .
```

### 发布新版本

1. 更新版本号（pyproject.toml, __init__.py）
2. 更新 CHANGELOG.md
3. 构建：`make build`
4. 发布：`python -m twine upload dist/*`

## 未来优化方向

1. **配置文件加载**: 实现config.yaml的自动加载
2. **日志系统**: 使用Python logging替代print
3. **异步支持**: 考虑asyncio改造（大规模并发）
4. **插件系统**: 支持自定义ping方法
5. **Web界面**: FastAPI后端 + Vue前端
6. **容器化**: Docker镜像和Kubernetes部署

## 参考资料

- [PEP 621 - Python Project Metadata](https://peps.python.org/pep-0621/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Src Layout vs Flat Layout](https://blog.ionelmc.ro/2014/05/25/python-packaging/)
- [pytest Documentation](https://docs.pytest.org/)

