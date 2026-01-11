# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Web界面开发
- 异步支持（asyncio）

## [2.2.0] - 2026-01-11

### Added - 新增功能
- ✨ 新增 `env/` 目录，独立管理项目环境配置
- ✨ 环境配置文件独立化，每个项目一个 YAML 文件
- ✨ 三步式交互流程：选择环境 → 选择 Sheet → 颜色过滤
- ✨ 自动扫描 `env/` 目录加载所有环境配置
- ✨ **新增 `ping-env-add` 命令**：快速创建环境配置
- ✨ 新增环境配置文档 `env/README.md`
- ✨ 新增详细交互流程文档 `docs/INTERACTIVE_FLOW.md`

### Changed - 变更
- 🔨 重构 `ConfigManager` 从目录扫描加载配置，而非单文件
- 🔨 配置文件从 `configs/ip_planning_profiles.yaml` 迁移到 `env/*.yaml`
- 🔨 简化环境配置格式，只需要 `name` 和 `file` 两个字段
- 🔨 交互式流程重新设计，更适合非技术用户

### Improved - 优化
- ⚡ 环境管理更灵活，添加新项目只需创建新文件
- ⚡ 配置结构更清晰，`configs/` 放应用配置，`env/` 放环境配置
- ⚡ Sheet 选择改为必选，避免误操作
- ⚡ 交互提示更友好，步骤更明确

### Removed - 移除
- ❌ 删除 `configs/ip_planning_profiles.yaml` 配置文件
- ❌ 移除 YAML 文件中冗余的配置项（sheet、color_filter 等）

## [2.1.0] - 2026-01-10

### Added - 新增功能
- ✨ 新增 IP 地址规划表 Ping 工具（`ping-ip-planning` 命令）
- ✨ 支持从 Excel 的 `net&sec` 和 `服务器&安全` sheet 读取 IP
- ✨ 自动读取 MGMT 列的 IP 和 hostname 列的主机名
- ✨ 支持按单元格颜色过滤（如只 ping 绿色单元格）
- ✨ 自动排除删除线的 IP 地址
- ✨ 添加 `python-calamine` 引擎支持，提升 Excel 读取兼容性
- ✨ 新增 `excel_reader.py` 模块处理 Excel 格式读取
- ✨ 支持 `--list-colors` 参数查看可用颜色
- ✨ 支持 `--local` 参数强制使用本地 ping
- ✨ 支持 `--max-workers` 参数自定义并发数

### Changed - 变更
- 🔨 更新 requirements.txt 添加 python-calamine 依赖
- 🔨 更新 pyproject.toml 添加新的命令行入口点
- 🔨 扩展文档说明新功能的使用方法

### Improved - 优化
- ⚡ 使用 calamine 引擎读取 Excel，提升兼容性
- ⚡ 批量读取单元格样式，提升性能
- ⚡ 优化日志输出，同时显示 IP 和 hostname

### Fixed - 修复
- 🐛 解决某些 Excel 文件格式导致 openpyxl 无法读取的问题

## [2.0.0] - 2025-11-12

### Added - 新增功能
- ✨ 采用专业Python项目架构（src-layout）
- ✨ 创建完整的pyproject.toml配置（PEP 621）
- ✨ 模块化设计：core、utils、models分层
- ✨ 完整的pytest测试框架
- ✨ SSH连接池机制，支持并发远程测试
- ✨ 示例文件系统（examples/目录）
- ✨ 配置管理系统（configs/config.yaml）
- ✨ Makefile快捷命令
- ✨ 完善的文档体系（INSTALL、DEVELOPMENT、ARCHITECTURE）
- ✨ 多种运行方式（模块、命令、兼容脚本）

### Changed - 变更
- 🔨 重构单文件脚本为模块化架构
- 🔨 重构ping功能到独立模块（core/ping.py）
- 🔨 重构SSH连接到独立模块（core/ssh.py）
- 🔨 优化延迟分析为独立工具函数（utils/analysis.py）
- 🔨 改进凭证管理（utils/credentials.py）
- 🔨 统一日志目录为logs/（原log/）

### Improved - 优化
- ⚡ 本地测试：20线程并发
- ⚡ 远程测试：5线程并发（避免SSH限制）
- ⚡ 网段测试：30线程并发（本地）/ 5线程（远程）
- ⚡ Ping参数优化：`-c 3 -W 2 -i 0.2`
- ⚡ SSH连接重试机制（最多2次）
- ⚡ 递增延迟避免连接风暴

### Fixed - 修复
- 🐛 修复SSH并发连接限制导致的连接失败问题
- 🐛 修复Excel整数密码的.0后缀问题
- 🐛 修复密码和用户名类型转换问题
- 🐛 修复空值处理问题

### Security - 安全
- 🔒 完善.gitignore保护敏感数据
- 🔒 分离示例文件和真实凭证
- 🔒 禁用paramiko详细日志输出

### Documentation - 文档
- 📚 完善README添加快速开始
- 📚 创建INSTALL.md安装指南
- 📚 创建DEVELOPMENT.md开发指南
- 📚 创建ARCHITECTURE.md架构文档
- 📚 创建examples/README.md示例说明
- 📚 创建REFACTORING_SUMMARY.md重构总结

### Deprecated - 废弃
- ⚠️ 废弃ping_v2.py直接运行方式（保留兼容）

### Removed - 移除
- 🗑️ 删除冗余目录（keys/, scripts/, data/, log/）
- 🗑️ 删除根目录重复文件（credentials.xlsx）
- 🗑️ 删除Python缓存文件

## [1.0.0] - 2025-11-10

### Added
- 🎉 初始版本发布
- ✅ 基础ping功能
- ✅ SSH远程测试支持
- ✅ Excel配置文件读取
- ✅ 延迟分析功能
- ✅ 日志输出功能

### Features
- 支持单个IP和网段测试
- 支持本地和远程测试
- 延迟统计（min/avg/max/mdev）
- 高延迟IP识别（>1ms）

---

## 版本说明

### 版本号规则
遵循[语义化版本](https://semver.org/lang/zh-CN/)：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的bug修复

### 变更类型说明

- `Added` - 新增功能
- `Changed` - 功能变更
- `Deprecated` - 即将废弃的功能
- `Removed` - 已删除的功能
- `Fixed` - Bug修复
- `Security` - 安全相关
- `Improved` - 性能优化
- `Documentation` - 文档更新

### Emoji图例

- ✨ 新功能
- 🔨 重构
- ⚡ 性能优化
- 🐛 Bug修复
- 🔒 安全相关
- 📚 文档
- 🎉 重大更新
- ⚠️ 警告/废弃
- 🗑️ 删除

---

## 路线图

### v2.1.0（计划中）
- [ ] 增加测试覆盖率到80%+
- [ ] 集成CI/CD（GitHub Actions）
- [ ] 添加命令行参数支持
- [ ] 配置文件自动加载
- [ ] 日志系统优化（使用logging模块）

### v2.2.0（计划中）
- [ ] Web界面（FastAPI + Vue）
- [ ] 实时监控功能
- [ ] 定时任务支持
- [ ] 邮件通知功能

### v3.0.0（远期）
- [ ] 异步重构（asyncio）
- [ ] 插件系统
- [ ] Docker容器化
- [ ] Kubernetes部署支持
- [ ] 发布到PyPI

---

## 贡献指南

查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目贡献代码。

## 许可证

本项目采用 [MIT License](LICENSE)。

