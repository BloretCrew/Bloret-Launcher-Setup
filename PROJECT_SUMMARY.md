# BLsetup 重写项目总结

本分支将旧版页面内副作用重写为 Windows x64 安装器架构。最终用户只获得一个 `BloretLauncherSetup.exe`。

## 当前已实现

- 无 UI 的领域状态机和 `InstallRunner` 编排器
- 可注入的环境预检、manifest 获取、下载、SHA-256 校验、ZIP 安全解包、原子安装、备份回滚
- `file://` manifest/package 离线测试注入，不使用生产下载 URL
- 取消、失败、可恢复错误、恢复 marker 和单实例锁边界
- Windows x64 平台检查、默认 `%APPDATA%` 安装目录、用户缓存目录
- 快捷方式适配器边界：仅 Windows 且依赖可用时执行，不伪造跨平台成功
- PyQt UI 仅展示领域事件并触发 runner；PyQt 缺失时模块仍可安全导入，只有启动 GUI 时失败
- Blora Design 2.x 官方语义 token 名称映射。PyQt 不直接渲染 Web Custom Elements，适配边界见 `ARCHITECTURE.md`
- 唯一 PyInstaller Windows x64 构建 workflow，构建 smoke test 要求 `dist` 只有一个 EXE

## 离线验证

```bash
python -m py_compile installer.py blsetup/*.py tests/*.py
python -m unittest discover -s tests -p 'test_*.py'
python installer.py --smoke-test
```

如安装环境没有 pytest，使用上述 `unittest` 或自包含临时目录 smoke test。测试不得访问生产 URL、真实安装目录、真实包或凭据。

## 明确未完成/未验证

Linux 上无法验证 Windows GUI、UAC 提权、真实 Windows 单实例语义、Registry、快捷方式实际创建、安装/卸载/升级、崩溃后恢复、Windows x64 PyInstaller 运行、代码签名、Defender/SmartScreen 和视觉快照。签名配置仅作 CI 占位检查，当前不能声称 EXE 已签名。

根目录旧页面、`.ui` 和历史测试保留作迁移参考，不属于新入口；CI 只发现 `tests/` 下的新离线测试，旧脚本不会被静默混入新测试套件。
