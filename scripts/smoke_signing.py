#!/usr/bin/env python3
"""用一次性密钥验证 Release 构建和签名；不读取正式 Secrets，不发布 APK。"""
import os
from pathlib import Path
import secrets
import subprocess
import tempfile

from verify_apk import verify


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sdk = Path(os.environ["ANDROID_HOME"])
    with tempfile.TemporaryDirectory(prefix="yuki-signing-", dir=os.environ.get("RUNNER_TEMP")) as directory:
        key = Path(directory) / "smoke.jks"
        password = secrets.token_urlsafe(32)
        env = os.environ | {
            "RELEASE_STORE_FILE": str(key),
            "RELEASE_STORE_PASSWORD": password,
            "RELEASE_KEY_ALIAS": "smoke",
            "RELEASE_KEY_PASSWORD": password,
        }
        subprocess.run([
            "keytool", "-genkeypair", "-noprompt", "-keystore", str(key),
            "-alias", "smoke", "-storepass:env", "RELEASE_STORE_PASSWORD",
            "-keypass:env", "RELEASE_KEY_PASSWORD", "-keyalg", "RSA", "-keysize", "2048",
            "-validity", "1", "-dname", "CN=Disposable CI test",
        ], check=True, env=env)
        subprocess.run([
            str(root / "gradlew"), "--no-daemon", "--stacktrace", ":app:assembleRelease",
        ], check=True, env=env, cwd=root)
        apk = root / "app/build/outputs/apk/release/app-release.apk"
        verify(apk)
        subprocess.run([str(sdk / "build-tools/37.0.0/apksigner"), "verify", "--verbose", str(apk)], check=True)
    print("Disposable Release signing check passed; temporary key removed.")


if __name__ == "__main__":
    main()
