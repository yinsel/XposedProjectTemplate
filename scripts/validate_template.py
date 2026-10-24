#!/usr/bin/env python3
"""验证模块配置、发布标签与源码目录中的旧入口残留。"""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
KEYS = {
    "module.applicationId", "module.name", "module.description", "module.versionCode",
    "module.versionName", "hook.targetPackage", "hook.targetClass", "hook.targetMethod",
}


def read_properties(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        key, separator, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not separator or not value or key in result or "\\" in value:
            raise ValueError(f"Invalid or duplicate property: {key}")
        result[key] = value
    return result


def validate(root: Path, tag: str | None = None) -> dict[str, str]:
    config = read_properties(root / "template.properties")
    if set(config) != KEYS:
        raise ValueError(f"Invalid property keys: {sorted(set(config) ^ KEYS)}")
    for key in ("module.applicationId", "hook.targetPackage"):
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+", config[key]):
            raise ValueError(f"Invalid package: {key}")
    if config["module.applicationId"] == config["hook.targetPackage"]:
        raise ValueError("Module and host must have different application IDs")
    if not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*(\.[A-Za-z_$][A-Za-z0-9_$]*)+", config["hook.targetClass"]):
        raise ValueError("Invalid hook.targetClass")
    if not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", config["hook.targetMethod"]):
        raise ValueError("Invalid hook.targetMethod")
    if not config["module.versionCode"].isdigit() or not 1 <= int(config["module.versionCode"]) <= 2100000000:
        raise ValueError("versionCode must be an integer in 1..2100000000")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?", config["module.versionName"]):
        raise ValueError("versionName must look like 1.0.0 or 1.0.0-rc.1")
    if tag is not None and tag != "v" + config["module.versionName"]:
        raise ValueError("Release tag must equal v + module.versionName")
    forbidden = list((root / "app/src").glob("**/assets/xposed_init"))
    forbidden += list((root / "app/src").glob("**/resources/META-INF/xposed/*"))
    if forbidden:
        raise ValueError("Remove source-tree Xposed metadata; YukiHook 1.5 generates it under build/")
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag")
    args = parser.parse_args()
    try:
        result = validate(ROOT, args.tag)
    except ValueError as error:
        parser.exit(1, f"Configuration error: {error}\n")
    print(f"Template OK: {result['module.applicationId']} {result['module.versionName']}")
