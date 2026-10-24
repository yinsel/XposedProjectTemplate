# 开发与调试

## 从示例到实际宿主

1. 保持默认配置，完成测试宿主的安装与 Hook 验收，确认框架和设备可用。
2. 修改 `template.properties` 中的 `module.*` 和 `hook.*`。版本名采用 `1.0.0` 或 `1.0.0-rc.1`；文件为 UTF-8、每行 `key=value`，不使用反斜杠转义或续行。
3. 根据实际反编译结果修改 `GreetingHooker` 的参数、返回类型和回调。示例只处理无参数 String 方法，并不自动适配任意目标。
4. 多功能模块按目标或功能新增 `YukiBaseHooker`，在 `HookEntry` 中通过 `loadHooker` 装载。只在确认需要时增加次进程路由。
5. 运行检查，安装新模块，在管理器中确认新作用域，强制停止并重新启动宿主。

`hook.targetPackage` 同时生成 BuildConfig 常量和 LSPosed 建议作用域，避免修改一处却遗漏另一处。管理器可能保留旧的用户选择，重新安装后仍需检查。`module.applicationId` 与 namespace 分离，因此改 ID 不需要移动源码。示例宿主 ID 固定为 `com.example.xposed.demo`。

## 代码示例

基于默认 Hooker 的 `firstMethod { ... }.hook { ... }`，可选择下列回调之一。不要直接复制签名条件到不同类型的方法。

```kotlin
// 无参 String 方法：替换返回值。
intercept("Hello from YukiHook!")

// 有参数方法：先在 firstMethod 中声明 parameters(String::class)。
before {
    firstArg().set("new argument")
}
```

查找宿主类使用 YukiHook 的 `toClass()` 扩展，其解析使用当前宿主 ClassLoader。不要使用模块自身 `Class.forName` 直接查找宿主私有类。类由动态 DEX 或加固 ClassLoader 加载时，应在确认真实加载时机后装载 Hook；`withApplicationReady` 适用于等待 Application 的情况，不保证所有动态代码已出现。

## 构建检查

```bash
python3 scripts/validate_template.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
./gradlew clean testDebugUnitTest lintDebug assembleDebug assembleRelease
python3 scripts/verify_apk.py app/build/outputs/apk/debug/app-debug.apk app/build/outputs/apk/release/app-release-unsigned.apk
```

APK 检查读取真实 ZIP 与 DEX 类定义，确认唯一的生成入口已打包，且没有把 Xposed API 类打包进去。宿主单元测试检查目标方法的反射签名及未 Hook 时的返回值。这些检查不能代替有 Xposed 框架的设备验收。

Debug 使用 Android 标准调试签名。不同机器和 CI 的 Debug 密钥可能不同，覆盖安装可能提示签名不一致；可卸载旧调试版本后重新安装，或使用自己统一的开发密钥。正式版本始终使用同一受控密钥。

## 常见问题

| 现象 | 排查方向 |
| --- | --- |
| 管理器不识别模块 | 检查 APK `assets/xposed_init`、生成类及合并 Manifest；不得保留旧源码入口 |
| 模块已激活但宿主不变 | 检查作用域、进程、类名、重载签名；强制停止宿主并查看 `YukiTemplate` 日志 |
| ClassNotFound | 核对宿主版本、ClassLoader、动态加载时机，模块不应依赖宿主 APK |
| KSP 报入口冲突 | 每个变体只保留一个注解和一个 runtime，删除源码中的 Xposed 元数据 |
| Gradle 同步失败 | 检查 JDK 17、AGP 对应 IDE、SDK 37；再按国内网络文档切源 |
| Release 无法安装 | 默认本地 Release 未签名；按发布指南提供四个环境变量 |

默认未启用 R8，以便逆向、调试与生成入口验证。若启用混淆，应基于实际生成代码补充保留规则，验证模块状态、入口和运行时 Hook，不能仅以编译成功作为验收。
