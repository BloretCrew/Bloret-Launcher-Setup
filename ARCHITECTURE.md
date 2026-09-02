# BLsetup 2.x 架构与阶段一盘点

## 范围

当前重写只支持 Windows x64。最终用户只接触一个 `BloretLauncherSetup.exe`；Bootstrapper、Installer Core、Update/Recovery Engine、Renderer/UI 和必要的提权逻辑均为同一 PyInstaller EXE 的内部模块/资源。Linux 仅用于离线测试和静态验证，不承诺运行 GUI 或安装行为。

## 旧实现盘点

旧入口是 `installer.py`，页面模块为 `page1.py`、`page2_1.py`、`page2_2.py`、`page3.py`。旧流程由页面直接控制：欢迎页触发快速/自定义安装，路径页写入配置，选项页收集快捷方式选项，进度页启动线程并模拟步骤或解压 ZIP 后复制文件。旧入口包含网络 Logo 请求、页面内下载/解压/复制、覆盖目标文件和进程启动等副作用；没有 manifest schema、包 hash、签名校验、原子替换或可靠 rollback。现有 `*.ui`、`scripts/` 和旧页面仅作为历史参考，阶段三入口不会调用它们。

现有 `Bloret-Launcher-Installer.spec` 与 `.github/workflows/build.yml` 会打包旧入口，并额外复制源码/资源，违反“单一用户交付 EXE”目标；阶段四将替换为只产出一个 EXE 的规则。`build/`、`dist/`、`__pycache__/`、日志和真实包均不应进入提交。

## 分层边界

```text
单一 EXE
├── Bootstrapper: 单实例、Windows x64 自检、生命周期与必要提权
├── Renderer/UI: PyQt 展示 InstallEvent，只发白名单命令
├── Installer Core: manifest、下载、hash/签名、解包、原子安装
└── Update/Recovery Engine: 快照、备份、回滚、残留清理、恢复标记
```

UI 不访问文件系统、Registry、PowerShell 或进程。副作用服务通过依赖注入，领域层保持可离线测试。提权只在执行确需权限的安装动作前发生；默认安装目录使用 `%APPDATA%` 下的产品目录，用户数据与安装缓存分离。

## 领域状态机

```text
CHECKING -> RESOLVING -> PREPARING -> DOWNLOADING -> VERIFYING -> INSTALLING -> COMPLETED
     \__________________________ FAIL (可回滚时进入 ROLLING_BACK) -> FAILED
任意非终态 -- CANCEL --> CANCELLED
FAILED -- RETRY --> CHECKING
```

状态事件包含稳定状态名、双语文案、可选进度、可恢复标记、错误 ID 和结构化详情。下载阶段允许重复 `DOWNLOAD_PROGRESS`。每个状态的输入/输出由命令表示：环境检查通过 `CHECK_OK`，清单通过 `MANIFEST_OK`，准备完成 `PREPARED`，下载完成 `DOWNLOAD_OK`，校验通过 `VERIFY_OK`，安装成功 `INSTALL_OK`；失败可携带 rollback/recoverable/error_id。

## 数据与安全决策

- manifest 固定带 `schema_version`、版本、包 URL、大小、SHA-256，未来签名字段采用向后兼容的新增 schema；未知必需版本拒绝安装。
- URL、目标目录、清单条目和包大小由 Core 校验；ZIP 条目必须规范化后仍位于临时目录，拒绝绝对路径、`..` 穿越、符号链接和超出大小上限的包。
- 下载写入隔离缓存的临时文件，完成 hash 校验后才进入安装；安装先生成快照，再将 staging 目录原子替换为目标目录，失败恢复备份。
- 单实例锁、取消、崩溃和重启恢复由 Bootstrapper/Recovery Engine 处理；网络失败和可恢复校验失败显示可重试错误，不自动执行未授权命令。
- 日志只记录结构化阶段和错误 ID，不写入凭据；面向用户的错误信息不得泄露完整本地路径。

## Blora Design 2.x 适配边界

已从 `/data/blora-design/packages/tokens/src/semantic/` 确认实际 token 名称，包括 `--blora-color-surface-canvas`、`--blora-color-surface-default`、`--blora-color-text-primary`、`--blora-color-text-secondary`、`--blora-color-action-primary-default`、`--blora-color-status-danger/success/warning`，以及 layout 的 `--blora-control-*` 和 `--blora-button-*` 语义。PyQt 桌面程序不能直接消费 Web Custom Elements 或浏览器 cascade layers，因此 UI 适配层保留官方 token 名称作为常量/样式映射，不伪造 Custom Element；最终渲染使用 Qt stylesheet 的等价值。组件行为边界记录在 UI 代码和 README 中。

阶段一未在 Windows 上验证 GUI、提权、Registry、快捷方式、签名、Defender/SmartScreen、安装/卸载和真实打包 EXE；这些是阶段四的明确未验证项，Linux 只运行离线 pytest/py_compile。
