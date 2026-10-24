# Agent 开发约定

## 项目边界

- 首先阅读 `README.md`、`template.properties`、`gradle/libs.versions.toml`。
- `app` 是模块；`demo-app` 是独立宿主。不要让模块依赖宿主项目，否则无法检验真实 ClassLoader 边界。
- 使用 YukiHook 1.5 API：`YukiHookXposedModule`、`@YukiHookXposed82Entry`、KavaRef。不要加入过时的 `InjectYukiHookWithXposed`、`IYukiHookXposedInit` 或旧 `method {}` 反射 API。
- `HookEntry` 只做初始化与路由，每项功能使用独立 `YukiBaseHooker`。默认仅 Hook 指定包的主进程。
- 不提交 `assets/xposed_init`、KSP 产物、APK、SDK 路径、签名密钥或密码。不要关闭签名、证书或 Gradle 分发校验来解决下载问题。

## 修改策略

- 修改 applicationId、版本、名称、目标时优先编辑 `template.properties`。不要误把源码 namespace 当作 applicationId。
- 目标类必须通过宿主 ClassLoader 查找，精确限制参数和返回类型。查找失败要保留宿主原行为并记录可诊断信息。
- 不缓存 Activity/Context，不在 Hook 回调中执行网络或耗时 I/O，不记录宿主敏感业务数据。
- 一次构建只使用一个 runtime，Xposed API 只用 `compileOnly`。
- AGP 9 自带 Kotlin。不要额外应用 `org.jetbrains.kotlin.android`。
- 不使用 `+`、SNAPSHOT 等动态依赖。升级 YukiHook 时统一 BOM 与 compiler；检查 AGP、Gradle、Kotlin、KSP、SDK 的兼容性。
- 本地默认国内源。GitHub Actions 的 Build 矩阵验证两种源，Release 使用官方源；runner 中的临时切源修改不应提交回来。

## 验证命令

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
./gradlew --no-daemon clean testDebugUnitTest lintDebug assembleDebug assembleRelease
python3 scripts/verify_apk.py app/build/outputs/apk/debug/app-debug.apk app/build/outputs/apk/release/app-release-unsigned.apk
git diff --check
```

若 SDK、网络或设备不可用，应明确报告未完成的检查，不得把静态检查描述为编译通过。真实 Hook 验收必须执行 README 的设备步骤。签名 Release 的输出为 `app-release.apk`，不要与默认未签名输出混淆。

## 交付说明

说明修改目的、受影响文件、实际执行的检查和结果。除非用户明确要求，不推送发布标签、不发布 Release、不合并主分支。开发提交可以推送到任务分支。
