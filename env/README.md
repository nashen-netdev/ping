# 环境配置目录

这个目录存放各个项目的环境配置文件。

## 📁 文件说明

每个 `.yaml` 文件代表一个项目环境，文件名即为环境名。

### 配置格式

```yaml
# 环境显示名称
name: "项目名称"

# Excel 文件路径
file: "pass/IP地址规划表-xxx.xlsx"
```

## 📝 示例

**`jinmao.yaml`**
```yaml
name: "金茂"
file: "pass/IP地址规划表-金茂1.xlsx"
```

## ➕ 如何添加新环境

### 方法 1：使用命令（推荐，最简单）

```bash
# 基本用法
ping-env-add bj08 /path/to/IP地址规划表-金茂1.xlsx

# 指定显示名称
ping-env-add sh01 pass/file.xlsx --display-name "上海01机房"
```

### 方法 2：手动创建文件

1. 在此目录下创建新的 `.yaml` 文件
2. 文件名使用英文（将作为环境 ID）
3. 填写配置内容

例如，添加 "新项目"：

```bash
# 创建文件 env/newproject.yaml
cat > env/newproject.yaml << 'EOF'
name: "新项目"
file: "pass/IP地址规划表-新项目.xlsx"
EOF
```

## 🗑️ 如何删除环境

直接删除对应的 `.yaml` 文件即可。

## 📋 当前环境列表

- `jinmao.yaml` - 金茂项目
- `xxidc.yaml` - xxidc 项目
- `xxproject.yaml` - xx 项目

## 🔍 查看所有可用环境

```bash
ping-ip-planning --list-profiles
```

## ⚠️ 注意事项

1. 文件名不要包含空格和特殊字符
2. 确保 `file` 路径正确
3. 修改配置后无需重启，下次运行自动生效
