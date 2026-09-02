# Bloret Launcher Setup

Windows x64 安装器（重写版）。用户交付物只有一个 `BloretLauncherSetup.exe`，内部包含 UI、Installer Core 和恢复逻辑；不要求用户单独下载或运行 bootstrapper/helper/update.exe。

## 开发验证

Linux 开发机不能运行 Windows GUI、Windows 提权、Registry、快捷方式或 Defender/SmartScreen。可执行以下离线验证：

```bash
python -m py_compile installer.py blsetup/*.py tests/*.py
python -m unittest discover -s tests -p 'test_*.py'
```

测试只使用临时目录、伪造 ZIP 和本地 `file://` 清单，不访问生产下载源、不覆盖真实安装目录。若环境未安装 pytest，可使用仓库 CI 的 Windows smoke test。

## 架构与安全

详见 [`ARCHITECTURE.md`](ARCHITECTURE.md)。安装流程由无 UI 领域状态机驱动：环境检查、清单解析、准备、下载、SHA-256 校验、原子替换、备份和回滚。ZIP 解包拒绝路径穿越、符号链接和超出大小限制的内容。

PyQt 不能直接使用 Web Custom Elements 或 CSS cascade layers，因此 `blsetup/tokens.py` 保留 Blora Design 2.x 官方语义 token 名称，并在 Qt stylesheet 中进行有限的值映射。这是适配边界，不是对 Web 组件 API 的模拟；实际 token 来源已在架构文档中记录。

## 构建

在 Windows x64 上运行：

```powershell
python -m pip install pyinstaller PyQt5
pyinstaller --clean --noconfirm BloretLauncherSetup.spec
```

发布目录必须且只能有 `dist/BloretLauncherSetup.exe`。不要提交 `build/`、`dist/`、`__pycache__/`、日志、缓存、真实安装包、凭据或签名密钥。CI 会检查该单一产物规则。

## Windows 未验证项

当前 Linux 环境未验证真实 Windows GUI 渲染、系统/架构检查、UAC 提权、单实例锁、Registry/快捷方式、安装/卸载/升级、签名、Windows Defender/SmartScreen、崩溃重启恢复及最终 EXE 的视觉快照。这些必须在受控 Windows x64 机器上完成验收后才能宣称发布就绪。
