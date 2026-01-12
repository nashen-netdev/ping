# Scripts 目录说明

本目录包含项目维护和管理脚本。

## 可用脚本

### 1. `clean_logs.sh` - 日志清理脚本

清理指定天数前的日志文件。

**使用方法**：

```bash
# 清理 7 天前的日志（默认）
./scripts/clean_logs.sh

# 清理 3 天前的日志
./scripts/clean_logs.sh 3

# 清理 30 天前的日志
./scripts/clean_logs.sh 30
```

**功能**：
- 自动查找 logs/ 目录中的 .log 文件
- 按修改时间过滤
- 删除前会显示文件列表并要求确认
- 显示清理统计信息

**示例输出**：

```
================================================
日志清理脚本
================================================
项目目录: /Users/sen/automate/Network_Projects/ethernet/ping
日志目录: /Users/sen/automate/Network_Projects/ethernet/ping/logs
清理策略: 删除 7 天前的日志文件
================================================

当前日志文件数量: 4
需要清理的日志数量: 2

将要删除以下日志文件:
----------------------------------------
  logs/ping_results.log (3.9K)
  logs/ping_results_old.log (5.2K)
----------------------------------------

确认删除这些文件？(y/n) [n]: y

正在删除旧日志...

✓ 清理完成！
  已删除: 2 个文件
  剩余: 2 个文件
```

**注意事项**：
- 删除操作不可恢复，请谨慎确认
- 脚本会保留 .gitkeep 文件
- 建议定期运行（如每周一次）

---

## Makefile 清理命令

除了直接运行脚本，也可以使用 Makefile 命令：

```bash
# 清理 Python 临时文件（.pyc, __pycache__, .DS_Store 等）
make clean

# 清理 7 天前的日志
make clean-logs

# 深度清理（临时文件 + 日志）
make clean-all
```

**Makefile 清理内容**：

| 命令 | 清理内容 |
|------|---------|
| `make clean` | Python 缓存、编译文件、系统临时文件 (.DS_Store, .swp, .bak, .tmp) |
| `make clean-logs` | 7 天前的日志文件 |
| `make clean-all` | 所有临时文件 + 日志 |

---

## 定期清理建议

### 手动清理

建议每周运行一次：

```bash
cd /Users/sen/automate/Network_Projects/ethernet/ping
make clean-all
```

### 自动清理（可选）

可以设置 cron 任务自动清理：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每周日凌晨 3 点清理）
0 3 * * 0 cd /Users/sen/automate/Network_Projects/ethernet/ping && make clean-logs
```

---

## 清理前的注意事项

1. **日志备份**：
   - 如果需要保留历史日志，请先备份
   - 重要的测试结果应该单独保存

2. **文件恢复**：
   - 删除的文件无法恢复
   - 确保已经查看或导出重要数据

3. **正在运行的程序**：
   - 清理前确保没有程序正在写入日志
   - 如果程序正在运行，建议等待完成后再清理

---

## 故障排查

### 问题 1：权限不足

```bash
chmod: Permission denied
```

**解决方法**：
```bash
chmod +x scripts/clean_logs.sh
```

### 问题 2：找不到日志目录

```bash
✗ 日志目录不存在
```

**解决方法**：
```bash
mkdir -p logs
```

### 问题 3：无法删除文件

```bash
rm: cannot remove 'xxx.log': Permission denied
```

**解决方法**：
```bash
# 检查文件权限
ls -l logs/

# 修改权限（如果需要）
chmod 644 logs/*.log
```

---

## 维护建议

1. **定期检查日志大小**：
   ```bash
   du -sh logs/
   ```

2. **查看最旧的日志**：
   ```bash
   find logs/ -name "*.log" -type f -printf '%T+ %p\n' | sort | head -5
   ```

3. **统计日志数量**：
   ```bash
   find logs/ -name "*.log" -type f | wc -l
   ```

4. **查看日志占用空间**：
   ```bash
   find logs/ -name "*.log" -type f -exec du -h {} \; | sort -h
   ```

---

## 相关文档

- [项目 README](../README.md)
- [Makefile](../Makefile)
- [.gitignore](../.gitignore)
