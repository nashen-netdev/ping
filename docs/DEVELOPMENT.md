# 开发指南

## 项目结构说明

```
ping/
├── src/ping_tool/        # 主包（src-layout）
│   ├── __init__.py       # 包初始化
│   ├── __main__.py       # 模块入口
│   ├── cli.py            # CLI主程序
│   ├── core/             # 核心功能
│   │   ├── ping.py       # Ping功能
│   │   └── ssh.py        # SSH连接
│   ├── utils/            # 工具函数
│   │   ├── analysis.py   # 延迟分析
│   │   ├── credentials.py # 凭证管理
│   │   └── network.py    # 网络工具
│   └── models/           # 数据模型（预留）
├── tests/                # 测试文件
├── configs/              # 配置文件
├── docs/                 # 文档
├── logs/                 # 日志输出
├── pass/                 # 凭证和密钥
├── pyproject.toml        # 项目配置
├── Makefile              # 快捷命令
└── README.md             # 项目说明
```

## 开发环境设置

```bash
# 1. 安装开发依赖
make install-dev

# 2. 配置pre-commit（可选）
pip install pre-commit
pre-commit install
```

## 开发工作流

### 1. 编写代码

遵循PEP 8规范，使用类型注解：

```python
def ping_ip_local(ip: str) -> tuple[str, bool, str]:
    """
    函数文档字符串
    
    Args:
        ip: IP地址
        
    Returns:
        tuple: (IP, 成功标志, 输出)
    """
    pass
```

### 2. 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试
python3 -m pytest tests/test_analysis.py -v

# 查看测试覆盖率
python3 -m pytest --cov=src/ping_tool --cov-report=html
open htmlcov/index.html
```

### 3. 代码检查

```bash
# 运行所有检查
make lint

# 单独运行
python3 -m flake8 src/
python3 -m mypy src/
```

### 4. 格式化代码

```bash
# 自动格式化
make format
```

## 添加新功能

### 1. 创建新模块

```bash
# 在适当位置创建新文件
touch src/ping_tool/utils/new_feature.py
```

### 2. 编写测试

```bash
# 创建对应测试文件
touch tests/test_new_feature.py
```

### 3. 更新__init__.py

将新功能添加到包导出：

```python
from .utils.new_feature import new_function

__all__ = [..., "new_function"]
```

## Git提交规范

使用语义化提交：

```bash
feat(module): 添加新功能
fix(module): 修复bug
docs: 更新文档
style: 代码格式
refactor: 重构代码
test: 添加测试
chore: 构建工具
```

## 发布流程

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 和 src/ping_tool/__init__.py

# 2. 更新CHANGELOG.md

# 3. 构建包
make build

# 4. 测试安装
pip install dist/ping_tool-X.X.X-py3-none-any.whl

# 5. 发布到PyPI（如需）
python3 -m twine upload dist/*
```

## 常见问题

### 导入错误

确保使用开发模式安装：
```bash
pip install -e .
```

### 测试失败

清理缓存后重试：
```bash
make clean
make test
```

