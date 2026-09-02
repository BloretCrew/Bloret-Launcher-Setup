# BLsetup 重写实施计划

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 基于 Blora Design 2.x 重写 `bloret-launcher-setup`，重新设计 Windows 安装/更新流程，移除旧版不可靠设计，并保持安装结果可验证、可恢复和可维护。

**Architecture:** 新建独立 rewrite 分支，尽量不在旧代码上打补丁。项目第一阶段只支持 Windows，不为 Linux/macOS 设计兼容层。整体采用“薄 UI + 可测试领域层 + 受控副作用适配层”的架构：UI 只展示状态并发出命令；流程编排器管理状态机；下载、清单、签名/hash 校验、文件替换、快捷方式、权限和回滚分别由独立服务负责。安装器与被安装的 Launcher 解耦，使用稳定的 manifest/schema 和版本化安装布局，避免 UI、下载逻辑、安装路径相互耦合。

**Windows Architecture:** Windows 版本明确拆成 Bootstrapper、Installer Core、Update/Recovery Engine、Renderer/UI 四层。Bootstrapper 负责启动、单实例、版本自检和必要的管理员权限提升；Installer Core 负责 manifest、下载、校验、解包、原子安装和 rollback；Update/Recovery Engine 负责安装前快照、失败恢复、残留清理和重启后恢复；Renderer 只通过受控 IPC 调用白名单命令，不直接访问文件系统、Registry、PowerShell 或进程。需要管理员权限的操作集中在最小化的 elevated helper 中，普通 UI 进程不以管理员权限运行。

**Tech Stack:** 以当前项目实际 Windows 技术栈为基础，接入 `/data/blora-design` 的 Blora Design 资源/API；具体运行时、打包方式、签名、安装目录和提权机制在 Task 1 只读确认后确定。

---

## 已执行的备份

当前代码已在 Git 中建立备份分支：

```text
backup/pre-blora-rewrite-2026-09-02
```

该分支只用于保留重写前状态，不在其上开发，不删除、不改写、不 push。

## 产品目标

### 新流程

1. 启动器自检：系统、架构、权限、磁盘空间、网络；
2. 读取并校验远程/本地版本清单；
3. 展示安装目标、版本、组件和磁盘占用；
4. 用户确认后开始下载；
5. 实时显示阶段、速度、进度、剩余空间和可取消状态；
6. 下载完成后校验 hash/签名；
7. 原子化安装或更新，失败可回滚；
8. 显示完成结果、安装目录和下一步操作。

### 明确移除旧设计

- 不复用旧版混杂在 UI 中的流程控制；
- 不让 UI 直接操作文件、进程或下载器；
- 不用不可解释的长流程 loading 页面；
- 不静默覆盖用户文件；
- 不在失败时只显示笼统错误；
- 不把下载、校验、安装多个阶段伪装成一个进度条；
- 不使用旧版 Blora 1.x 类名或全局初始化 API；
- 不通过硬编码颜色实现主题。

## 分阶段任务

### Task 1：旧项目与 Windows 行为盘点

只读检查所有源码、脚本、配置、资源和测试，输出旧流程状态机、文件操作、下载源、校验方式、安装路径、更新策略、错误恢复和现有 Windows 行为。标出将废弃的文件和可复用的纯逻辑。确认当前运行时、打包方案、安装目录、用户目录、Registry/快捷方式使用、进程启动方式、管理员权限和 Windows 版本/架构支持范围。

### Task 2：架构设计与边界冻结

在开始写 UI 前，确定并记录以下架构决策：Bootstrapper、Renderer/UI、Installer Core、Update/Recovery Engine、elevated helper 的进程边界；IPC 命令白名单和数据 schema；manifest/schema 版本策略；安装目录与用户数据目录；单实例锁；下载缓存和临时目录；安装前快照、原子替换和回滚策略；权限提升时机；日志与错误模型；网络不可用、取消、崩溃和重启恢复策略。输出架构图、状态转换图、关键接口和威胁模型，并明确哪些旧模块废弃、哪些纯函数可复用。

### Task 2：新领域层和状态机

建立与 UI 无关的安装流程状态机和接口：检查、解析、准备、下载、校验、安装、回滚、完成、失败、取消。每个状态定义输入、输出、可恢复性和用户可见文案。副作用通过依赖注入，方便临时目录测试。

### Task 3：下载、校验与原子安装服务

实现可取消下载、断点/重试策略、大小限制、hash/签名验证、临时文件、原子替换、备份和失败回滚。所有路径必须规范化并防止路径穿越；安装前后检查磁盘空间和权限。禁止使用真实生产下载或覆盖真实用户安装目录做测试。

### Task 4：Blora Design 2.x UI

以 `/data/blora-design` 为本地设计依据，使用 2.x tokens、`.blora-button`、`.blora-card`、`.blora-input`、progress/steps/alert 等正确组件。实现：欢迎页、环境检查、目标选择、下载进度、校验、安装结果、失败恢复。深色/浅色主题、键盘访问、焦点管理、响应式窗口都要覆盖。禁止 1.x API 和自写假组件。

### Task 5：流程桥接与错误处理

将 UI 状态订阅到领域层事件；统一 loading/error/cancel/retry；错误展示具体阶段、原因、建议和日志 ID，不泄露路径中的敏感信息。退出/重启后能恢复或明确重新开始。

### Task 7：Windows 打包与发布

只验证 Windows x64（其他架构和操作系统暂不支持）。确认安装包不携带开发机路径、凭据或测试数据；验证安装器签名、安装/卸载、升级覆盖、快捷方式、文件关联、Windows Defender/SmartScreen 相关发布要求和 CI 构建。补充 Windows smoke test。资源定位、用户目录、进程退出码和权限提升必须在真实 Windows 环境验证。

### Task 7：验收与文档

使用隔离临时目录、临时下载源、伪造清单和测试 hash 做成功、失败、取消、断点、损坏包、空间不足、权限不足、回滚和重复运行测试。真实启动打包应用做视觉验收，生成截图。更新 README、故障排查和开发文档。

## 验收门槛

- 新状态机有单元测试；
- 下载/校验/安装/回滚有隔离集成测试；
- 旧版危险路径不再被新入口调用；
- Blora Design 2.x 依赖和实际资源加载可证明；
- 无明文凭据和开发机绝对路径进入提交；
- Windows x64 构建、安装器签名和 CI 结果真实记录；
- 真实窗口截图确认关键页面、控件、错误态和进度态完整；
- 未验证事项明确列出，不用“看起来应该可以”替代。

## Git 纪律

- 当前开发分支：`rewrite/blora-design-2`；
- 备份分支：`backup/pre-blora-rewrite-2026-09-02`；
- 第一阶段平台范围：Windows x64；不实现 Linux/macOS 兼容层；
- 只 commit 不 push；
- 每个阶段独立提交；
- 不 reset，不删除备份分支；
- 不提交 `.env`、token、密钥、真实安装包、下载缓存或测试数据。
