# YukiHook Xposed 模块模板

<img src="app/src/main/res/mipmap-xxxhdpi/ic_launcher.webp" alt="模块图标" width="72" />

面向 Android 逆向工程师与编码 Agent 的 Kotlin 模块模板。参考 [YukiHook 官方 samples](https://github.com/HighCapable/YukiHook/tree/1.5.0/samples)，采用 **YukiHook 1.5.0 + Xposed 82 底座 + KavaRef + KSP**。

- **可以直接验证**：附带独立测试宿主，启用模块后将问候文字替换为 `Hello from YukiHook!`。
- **配置集中**：修改 `template.properties` 即可设置模块 ID、名称、版本和 Hook 目标；不需要批量替换源码包名。
- **国内源优先**：Gradle Wrapper 使用腾讯云镜像，Maven 使用阿里云与腾讯云镜像，提供官方源切换脚本。
- **自动构建与发布**：分支推送、PR 和手动触发构建；版本标签触发签名 APK 与校验文件发布。
- **适合 Agent**：提供 [AGENTS.md](AGENTS.md)、明确的代码边界、无 SDK 检查脚本和 APK 入口检查。

## 快速开始

需要 JDK 17、Python 3.10+、支持 AGP 9.3 的 Android Studio，以及 Android SDK Platform 37 / Build Tools 37.0.0。依赖版本与 YukiHook 1.5.0 官方示例对齐：

| 组件 | 固定版本 |
| --- | --- |
| Gradle | 9.8.1 |
| Android Gradle Plugin | 9.3.3 |
| Kotlin / KSP | 2.4.21 / 2.3.12 |
| YukiHook / KavaRef BOM | 1.5.0 / 1.1.1 |
| 最低运行版本 | Android 8.0 / API 26 |

1. 使用 GitHub 的 **Use this template**（仓库拥有者需先启用 Template repository），或克隆本仓库。
2. 用 Android Studio 打开根目录，指定 JDK 17，通过 SDK Manager 安装上述 SDK。无 IDE 时设置 `ANDROID_HOME`，或在不提交的 `local.properties` 中设置 `sdk.dir`。
3. 执行以下命令。Windows 将 `./gradlew` 替换为 `gradlew.bat`，将 `python3` 替换为 `py -3`。

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
./gradlew :app:assembleDebug :demo-app:assembleDebug
```

输出：

| APK | 用途 |
| --- | --- |
| `app/build/outputs/apk/debug/app-debug.apk` | 安装到已支持 Xposed 82 API 的设备上的模块 |
| `demo-app/build/outputs/apk/debug/demo-app-debug.apk` | 独立测试宿主 |

## 在设备上验证

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb install -r demo-app/build/outputs/apk/debug/demo-app-debug.apk
```

在 LSPosed 等兼容框架中启用模块，勾选 **YukiHook 测试宿主**（`com.example.xposed.demo`）。按框架要求重启设备，或强制停止宿主再启动：

```bash
adb shell am force-stop com.example.xposed.demo
adb shell am start -n com.example.xposed.demo/.MainActivity
adb logcat -s YukiTemplate
```

未启用时显示 `Hello from the demo app.`；启用后应显示 `Hello from YukiHook!`。模块管理页面显示的激活状态仅用于诊断，不等同于宿主 Hook 成功。

## 开发自己的模块

先修改 [template.properties](template.properties)，再运行配置检查。默认示例精确匹配“无参数、返回 String”的方法；接入实际宿主时需要同时修改方法签名与 Hook 逻辑。

| 位置 | 修改内容 |
| --- | --- |
| `template.properties` | 模块 applicationId、名称、说明、版本；目标包、类和方法 |
| `app/src/main/java/com/example/xposed/hook/HookEntry.kt` | 唯一入口，包名与主进程过滤 |
| `app/src/main/java/com/example/xposed/hook/GreetingHooker.kt` | KavaRef 查找和 YukiHook 回调 |
| `app/src/main/java/com/example/xposed/ui/MainActivity.kt` | 模块状态页面 |
| `demo-app/` | 独立测试宿主，不引用模块代码 |
| `gradle/libs.versions.toml` | 固定工具链和依赖版本 |
| `.github/workflows/` | 构建与发布流水线 |

源码 namespace 保持 `com.example.xposed`，与可配置的安装包名 applicationId 相互独立。KSP 自动从 BuildConfig 读取真实 applicationId；修改模块 ID 不需要手写注解参数。若还要重命名 namespace，请通过 IDE 重构源码包，并同步 `scripts/verify_apk.py` 中的入口断言。

> [!IMPORTANT]
> YukiHook 1.5 会在构建目录中生成 `assets/xposed_init`。不要在 `src/` 中手动创建入口文件，也不要混用旧版 `api` / `ksp-xposed` 依赖。Xposed API 必须使用 `compileOnly`。

更多操作参见 [开发指南](docs/development.md)、[国内网络配置](docs/china-build.md) 和 [发布指南](docs/releasing.md)。本模板默认使用 Xposed 82 底座；libxposed、热重载和远程配置不在默认实现范围内，可参照官方 modern 示例另行迁移。

## 自动构建与发布

`Build` 工作流在分支推送、PR 或手动运行时，分别使用国内源和官方源执行 Python 检查、单元测试、Lint、Debug/Release 编译和 APK 检查。官方源任务另用一次性密钥验证 Release 签名配置，测试密钥不会发布。成功后可从 Actions 下载模块和宿主的 Debug APK。普通构建不需要任何正式签名密钥。

正式发布需要先配置四项 GitHub Secrets，递增 `module.versionCode`，设置 `module.versionName`，提交后推送匹配的 `v版本号` 标签。`Release` 工作流验证签名并发布 APK 和 `SHA256SUMS.txt`，预发布版本会标记为 prerelease。完整步骤见 [发布指南](docs/releasing.md)。

## 参考资料

- [YukiHook 项目](https://github.com/HighCapable/YukiHook) / [中文文档](https://highcapable.github.io/YukiHook/zh-cn/)
- [固定版本官方 legacy 示例](https://github.com/HighCapable/YukiHook/tree/1.5.0/samples/demo-module-legacy)
- [官方 modern 示例](https://github.com/HighCapable/YukiHook/tree/1.5.0/samples/demo-module-modern)
- [YukiHook 1.5 迁移指南](https://highcapable.github.io/YukiHook/zh-cn/config/migration-1-5-x)
