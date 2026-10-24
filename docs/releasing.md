# 自动构建与正式发布

## 普通构建

`Build` 支持所有分支推送、PR 与 Actions 页的手动触发。Fork PR 也可以执行，不读取仓库 Secrets，不使用 `pull_request_target`。产物包含可安装的 Debug 模块和 Debug 宿主；Release 编译用于检查，未签名 APK 不作为可安装产物发布。

## 配置签名

在安全的本地环境生成并备份自己的密钥，交互输入密码，不将密码写入命令历史：

```bash
keytool -genkeypair -keystore release.jks -alias release -keyalg RSA -keysize 4096 -validity 10000
```

在仓库 Settings → Secrets and variables → Actions 添加：

| Secret | 内容 |
| --- | --- |
| `KEYSTORE_BASE64` | 密钥文件的单行 Base64 编码 |
| `RELEASE_STORE_PASSWORD` | 密钥库密码 |
| `RELEASE_KEY_ALIAS` | 密钥别名，例如 release |
| `RELEASE_KEY_PASSWORD` | 对应密钥密码 |

跨平台生成单行 Base64（输出文件包含完整密钥材料，上传后妥善删除）：

```bash
python3 -c "import base64,pathlib; pathlib.Path('keystore-base64.txt').write_text(base64.b64encode(pathlib.Path('release.jks').read_bytes()).decode())"
```

勿把该文本、keystore、密码或备份提交到 Git。仓库提供忽略规则，仍应在提交前检查文件列表。丢失密钥将无法覆盖升级已安装版本。

## 推送版本标签

1. 修改 `template.properties` 中的版本名，并递增整数版本号。
2. 提交到已经通过构建检查的分支。
3. 在需要发布的提交上创建并推送标签：

```bash
python3 scripts/validate_template.py --tag v1.0.0
git tag -a v1.0.0 -m 'Release 1.0.0'
git push origin v1.0.0
```

`Release` 会再次运行测试和 Release Lint，使用 Secrets 签名，检查 Xposed 入口和 APK 签名，然后创建 GitHub Release，上传 `module-v1.0.0.apk` 与 `SHA256SUMS.txt`。`v1.0.0-rc.1` 等带连字符的版本标记为预发布。缺少密钥或标签与配置不一致时会失败，不会退回 Debug 签名。

正式发布只上传模块，不发布测试宿主。流程不会替换现有 Release 的资源；若标签已有 Release，应检查现有结果并按需要发布新版本。不要移动已经发布的版本标签。首次启用 Actions 时，若仓库或组织策略禁止工作流写入 contents，应由维护者调整对应策略。

## 本地签名构建

通过本地安全环境注入以下变量，避免提交到 `gradle.properties`：

- `RELEASE_STORE_FILE`：密钥文件绝对路径，或相对仓库根目录的路径。
- `RELEASE_STORE_PASSWORD`、`RELEASE_KEY_ALIAS`、`RELEASE_KEY_PASSWORD`：与上表含义一致。

```bash
./gradlew :app:assembleRelease
python3 scripts/verify_apk.py app/build/outputs/apk/release/app-release.apk
```

四个变量必须同时存在。没有配置时，本地 `assembleRelease` 输出 `app-release-unsigned.apk`，用于检查或另行签名；不会使用硬编码密钥或 Debug 密钥。流水线始终删除 runner 临时密钥。
