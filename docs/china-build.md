# 国内网络构建

## 默认配置

| 内容 | 首选源 | 兜底 |
| --- | --- | --- |
| Gradle 9.8.1 分发 | `https://mirrors.cloud.tencent.com/gradle/` | 手动切换官方分发 |
| Google Maven | `https://maven.aliyun.com/repository/google` | Google Maven |
| Maven Central | `https://maven.aliyun.com/repository/central` | 腾讯 Maven public、Maven Central |
| Gradle 插件 | 阿里云 google、gradle-plugin、central | 官方 Plugin Portal |
| Xposed API 82 | 阿里云 public、腾讯 Maven public | `https://api.xposed.info/` |
| HighCapable 依赖 | 阿里云 / 腾讯 Central 镜像 | Maven Central、HighCapable 官方备用仓库 |

仓库顺序定义于 `settings.gradle.kts`。国内模式是“国内优先并保留官方兜底”，不承诺完全离线。Gradle 对网络超时、服务端错误或已有元数据但缺少文件的仓库，不一定自动切换下一源；遇到镜像同步延迟请显式切源。

## 切换方式

必须在首次启动 Wrapper 之前执行，脚本同时修改 Gradle 下载地址和 Maven 模式，保留固定版本及 SHA-256：

```bash
python3 scripts/configure_repositories.py --mode official
./gradlew --refresh-dependencies :app:assembleDebug

# 恢复默认国内源
python3 scripts/configure_repositories.py --mode china
```

Gradle 已下载完成后，也可仅切换依赖源：

```bash
./gradlew -PrepositoryMode=official :app:assembleDebug
```

该参数不会更改 Wrapper 分发地址。GitHub Actions 使用切源脚本，避免海外 runner 绕行国内镜像。

## 校验与代理

`gradle-wrapper.properties` 固定 `distributionSha256Sum`，值来自 [Gradle 官方 9.8.1 Release](https://github.com/gradle/gradle-distributions/releases/tag/v9.8.1) 的 bin 分发。镜像返回的内容必须与官方一致。升级时应同时更新 Wrapper JAR、启动脚本、URL 和校验值；不得删除校验以绕过不一致。

如需公司代理，可在用户目录的 `~/.gradle/gradle.properties` 中配置 `systemProp.https.proxyHost` / `systemProp.https.proxyPort`，不要把认证信息提交到仓库。Android SDK 是独立下载渠道，请通过 Android Studio SDK Manager 或官方 command-line tools 安装；Maven 镜像不能代替 SDK 平台与 Build Tools。

依赖源仍不可用时，使用 `--info --stacktrace` 定位具体坐标和 URL。不要引入来源不明的代理域名、关闭 HTTPS 校验或提交本机缓存。
