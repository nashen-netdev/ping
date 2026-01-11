# 环境配置管理指南

本文档介绍如何管理项目环境配置（`env/` 目录）。

---

## 📋 概述

环境配置用于存储不同项目的 Excel 文件路径信息。每个环境对应一个 YAML 配置文件。

### 目录结构

```
env/
├── jinmao.yaml      ← 金茂项目
├── xxidc.yaml       ← xxidc 项目
├── xxproject.yaml   ← xx 项目
└── README.md        ← 说明文档
```

### 配置格式

```yaml
# 项目显示名称
name: "项目名称"

# Excel 文件路径（绝对路径或相对路径）
file: "pass/IP地址规划表-xxx.xlsx"
```

---

## ➕ 添加新环境

### 方法 1：使用命令（推荐）

最简单快捷的方式：

```bash
# 基本用法
ping-env-add <环境ID> <文件路径>

# 示例：创建北京机房环境
ping-env-add bj08 /Users/sen/Desktop/IP地址规划表-金茂1.xlsx

# 指定友好的显示名称
ping-env-add bj08 ~/Desktop/file.xlsx --display-name "北京08机房"

# 使用相对路径
ping-env-add sh01 pass/IP地址规划表-上海.xlsx --display-name "上海01机房"
```

**输出示例：**

```
======================================================================
✅ 成功创建环境配置: bj08
======================================================================
  环境 ID: bj08
  显示名称: 北京08机房
  文件路径: /Users/sen/Desktop/IP地址规划表-金茂1.xlsx
  配置文件: /Users/sen/automate/.../env/bj08.yaml
======================================================================

💡 使用方法:
  ping-ip-planning           # 交互式选择，可以看到新环境
  ping-ip-planning --list-profiles  # 列出所有环境
```

### 方法 2：手动创建文件

如果你熟悉 YAML 格式，也可以手动创建：

```bash
# 1. 创建配置文件
cat > env/myproject.yaml << 'EOF'
name: "我的项目"
file: "pass/IP地址规划表-myproject.xlsx"
EOF

# 2. 验证配置
ping-ip-planning --list-profiles
```

---

## 📝 查看环境列表

### 命令行查看

```bash
# 列出所有环境
ping-ip-planning --list-profiles
```

**输出示例：**

```
可用的配置环境:
======================================================================
  • bj08     - 北京08机房: 无描述
  • jinmao   - 金茂: 无描述
  • sh01     - 上海01机房: 无描述
  • xxidc    - xxidc: 无描述
======================================================================
```

### 交互式查看

```bash
# 启动交互模式
ping-ip-planning

# 显示所有可选环境
可用的配置环境:
  1. 北京08机房
  2. 金茂
  3. 上海01机房
  4. xxidc
```

---

## ✏️ 修改环境配置

### 修改文件路径

```bash
# 1. 编辑配置文件
vi env/bj08.yaml

# 2. 修改 file 字段
file: "新的文件路径.xlsx"

# 3. 保存后立即生效，无需重启
```

### 修改显示名称

```bash
# 编辑配置文件
vi env/bj08.yaml

# 修改 name 字段
name: "新的显示名称"
```

---

## 🗑️ 删除环境

直接删除对应的 YAML 文件即可：

```bash
# 删除环境配置
rm env/bj08.yaml

# 验证已删除
ping-ip-planning --list-profiles
```

---

## 🔄 重命名环境

环境 ID（文件名）即为环境标识符，重命名需要：

```bash
# 重命名文件
mv env/old_name.yaml env/new_name.yaml

# 新环境 ID 立即生效
ping-ip-planning --list-profiles
```

---

## 📂 路径说明

### 绝对路径 vs 相对路径

**绝对路径**（推荐用于桌面文件）：

```yaml
file: "/Users/sen/Desktop/IP地址规划表-金茂1.xlsx"
```

**相对路径**（推荐用于项目内文件）：

```yaml
file: "pass/IP地址规划表-金茂1.xlsx"  # 相对于项目根目录
```

### 路径展开

支持 `~` 符号：

```yaml
file: "~/Desktop/IP地址规划表-金茂1.xlsx"
```

等价于：

```yaml
file: "/Users/sen/Desktop/IP地址规划表-金茂1.xlsx"
```

---

## 🔍 常见问题

### Q1: 创建环境时提示文件不存在？

**原因**：指定的 Excel 文件路径不存在。

**解决**：
1. 检查文件路径是否正确
2. 确认文件是否存在
3. 如果确定路径正确，可以选择继续创建（稍后移动文件到该路径）

```bash
⚠️  警告: Excel 文件不存在: /path/to/file.xlsx
是否继续创建配置？(y/n) [y]: y
```

### Q2: 环境 ID 已存在怎么办？

**提示**：

```
❌ 错误: 环境 'bj08' 已存在
   文件: /path/to/env/bj08.yaml
是否覆盖？(y/n) [n]:
```

**选择**：
- 输入 `y` 覆盖现有配置
- 输入 `n` 取消，使用不同的环境 ID

### Q3: 创建后立即可用吗？

**是的！** 配置文件创建后立即生效，无需重启任何服务。

```bash
# 创建后立即使用
ping-env-add bj08 /path/to/file.xlsx
ping-ip-planning  # 立即可以看到 bj08 环境
```

### Q4: 可以批量创建环境吗？

可以使用脚本批量创建：

```bash
#!/bin/bash
# 批量创建环境

ping-env-add bj01 pass/IP地址规划表-bj01.xlsx -n "北京01机房"
ping-env-add bj02 pass/IP地址规划表-bj02.xlsx -n "北京02机房"
ping-env-add sh01 pass/IP地址规划表-sh01.xlsx -n "上海01机房"
ping-env-add sh02 pass/IP地址规划表-sh02.xlsx -n "上海02机房"

echo "批量创建完成！"
ping-ip-planning --list-profiles
```

### Q5: 环境配置需要提交到 Git 吗？

**建议**：
- ✅ **提交**：示例环境（如 `jinmao.yaml`）
- ❌ **不提交**：个人测试环境

`.gitignore` 已配置为默认忽略 `env/*.yaml`，但保留 `jinmao.yaml`：

```gitignore
# 环境配置目录
env/*.yaml        # 忽略所有环境配置
!env/jinmao.yaml  # 但保留 jinmao.yaml 作为示例
!env/README.md    # 保留说明文档
```

---

## 🎯 最佳实践

### 1. 命名规范

**环境 ID**（文件名）：
- ✅ 使用英文小写、数字、下划线
- ✅ 简短有意义：`bj08`, `sh01`, `prod`, `test`
- ❌ 避免中文、空格、特殊字符

**显示名称**：
- ✅ 可以使用中文
- ✅ 清晰描述：`"北京08机房"`, `"生产环境"`, `"测试环境"`

### 2. 文件路径管理

**项目内文件**（推荐相对路径）：

```bash
ping-env-add prod pass/IP地址规划表-生产.xlsx -n "生产环境"
```

**外部文件**（使用绝对路径）：

```bash
ping-env-add temp ~/Desktop/临时测试.xlsx -n "临时测试"
```

### 3. 组织建议

按用途分类：

```
env/
├── prod.yaml        ← 生产环境
├── test.yaml        ← 测试环境
├── bj01.yaml        ← 北京机房
├── sh01.yaml        ← 上海机房
└── temp.yaml        ← 临时测试
```

---

## 📚 相关命令速查

```bash
# 创建环境
ping-env-add <id> <file> [-n "名称"]

# 列出环境
ping-ip-planning --list-profiles

# 使用环境（交互式）
ping-ip-planning

# 查看帮助
ping-env-add --help
ping-ip-planning --help
```

---

## 🔗 相关文档

- [env/README.md](../env/README.md) - 环境配置目录说明
- [INTERACTIVE_FLOW.md](INTERACTIVE_FLOW.md) - 交互式使用流程
- [README.md](../README.md) - 项目主文档

---

## 💡 小技巧

### 快速切换环境

```bash
# 保存常用环境的快捷方式
alias ping-prod="ping-ip-planning --profile prod"
alias ping-test="ping-ip-planning --profile test"

# 使用
ping-prod  # 直接使用生产环境配置
```

### 备份环境配置

```bash
# 备份所有环境配置
tar czf env-backup-$(date +%Y%m%d).tar.gz env/

# 恢复
tar xzf env-backup-20260111.tar.gz
```

### 分享环境配置

```bash
# 导出单个环境
cp env/bj08.yaml ~/Desktop/

# 分享给同事
# 同事只需将文件放到 env/ 目录即可使用
```

---

**环境配置管理现在变得非常简单！** 🎉
