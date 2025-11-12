## 安装指南

### 前置要求

- Python 3.8+
- 虚拟环境（推荐）

### 方法1：开发模式安装（推荐）

```bash
# 1. 克隆或进入项目目录
cd /path/to/ping

# 2. 创建虚拟环境
python3 -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 4. 安装项目（开发模式）
make install
# 或手动安装
python3 -m pip install -e .

# 5. 安装开发依赖（可选）
make install-dev
```

### 方法2：直接使用

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 直接运行
python3 ping.py
```

### 方法3：构建并安装

```bash
# 1. 构建包
make build

# 2. 安装whl文件
pip3 install dist/ping_tool-2.0.0-py3-none-any.whl
```

### 验证安装

```bash
# 如果使用开发模式安装，可以直接调用命令
ping-tool --help

# 或作为模块运行
python3 -m ping_tool
```

### 更新依赖

```bash
# 更新到最新版本
pip3 install --upgrade -e .
```

### 卸载

```bash
pip3 uninstall ping-tool
```

