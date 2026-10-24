#!/usr/bin/env python3
"""检查真正打包的入口与 DEX 类定义，避免 CI 产出无法加载的 Xposed 模块。"""
import argparse
from pathlib import Path
import re
import struct
import zipfile

ENTRY = "com.example.xposed.hook.HookEntry_YukiHookXposedInit"


def dex_classes(data: bytes) -> set[str]:
    if not data.startswith(b"dex\n"):
        raise ValueError("Invalid DEX header")

    def integer(offset: int) -> int:
        return struct.unpack_from("<I", data, offset)[0]

    strings, types = integer(60), integer(68)
    count, definitions = integer(96), integer(100)
    result = set()
    for index in range(count):
        type_index = integer(definitions + index * 32)
        string_index = integer(types + type_index * 4)
        offset = integer(strings + string_index * 4)
        while data[offset] & 0x80:  # 跳过 string_data_item 的 ULEB128 长度。
            offset += 1
        offset += 1
        result.add(data[offset:data.index(b"\0", offset)].decode("utf-8", errors="replace"))
    return result


def verify(path: Path) -> None:
    with zipfile.ZipFile(path) as apk:
        if apk.namelist().count("assets/xposed_init") != 1:
            raise ValueError("APK must contain exactly one assets/xposed_init")
        entries = apk.read("assets/xposed_init").decode("utf-8").splitlines()
        if [entry.strip() for entry in entries if entry.strip()] != [ENTRY]:
            raise ValueError(f"Unexpected Xposed entry: {entries}")
        classes = set()
        for name in apk.namelist():
            if re.fullmatch(r"classes\d*\.dex", name):
                classes.update(dex_classes(apk.read(name)))
        if "L" + ENTRY.replace(".", "/") + ";" not in classes:
            raise ValueError("Generated entry class is missing from DEX")
        if any(name.startswith("Lde/robv/android/xposed/") for name in classes):
            raise ValueError("Xposed API classes were packaged; use compileOnly")
    print(f"APK OK: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path, nargs="+")
    args = parser.parse_args()
    for apk in args.apk:
        verify(apk)
