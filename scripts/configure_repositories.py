#!/usr/bin/env python3
"""在第一次启动 Gradle 之前切换 Wrapper 与 Maven 源；只使用 Python 标准库。"""
import argparse
from pathlib import Path
import re


def configure(root: Path, mode: str) -> None:
    wrapper = root / "gradle/wrapper/gradle-wrapper.properties"
    properties = root / "gradle.properties"
    text = wrapper.read_text(encoding="utf-8")
    match = re.search(r"gradle-([0-9.]+)-bin\.zip", text)
    if not match:
        raise ValueError("Cannot determine the pinned Gradle version")
    base = "mirrors.cloud.tencent.com/gradle" if mode == "china" else "services.gradle.org/distributions"
    url = "https\\://" + base + "/gradle-" + match[1] + "-bin.zip"
    text, count = re.subn(r"^distributionUrl=.*$", lambda _: "distributionUrl=" + url, text, flags=re.M)
    if count != 1:
        raise ValueError("Expected one distributionUrl")
    config, count = re.subn(r"^repositoryMode=.*$", "repositoryMode=" + mode,
                           properties.read_text(encoding="utf-8"), flags=re.M)
    if count != 1:
        raise ValueError("Expected one repositoryMode")
    wrapper.write_text(text, encoding="utf-8")
    properties.write_text(config, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=["china", "official"])
    args = parser.parse_args()
    configure(Path(__file__).resolve().parents[1], args.mode)
    print("Repository mode:", args.mode)
