"""无需 Android SDK 的配置、入口及切源回归测试。"""
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zipfile

from configure_repositories import configure
from validate_template import ROOT, validate
from verify_apk import ENTRY, dex_classes, verify


def make_dex(descriptors):
    data = bytearray(112)
    data[:8] = b"dex\n035\0"
    string_offset = len(data)
    data.extend(bytes(4 * len(descriptors)))
    type_offset = len(data)
    for index in range(len(descriptors)):
        data.extend(struct.pack("<I", index))
    class_offset = len(data)
    for index in range(len(descriptors)):
        data.extend(struct.pack("<I", index) + bytes(28))
    for index, descriptor in enumerate(descriptors):
        struct.pack_into("<I", data, string_offset + index * 4, len(data))
        data.extend(bytes([len(descriptor)]) + descriptor.encode() + b"\0")
    for offset, value in [(60, string_offset), (68, type_offset), (96, len(descriptors)), (100, class_offset)]:
        struct.pack_into("<I", data, offset, value)
    return bytes(data)


class TemplateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["template.properties", "gradle.properties", "gradle/wrapper/gradle-wrapper.properties"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)

    def change(self, before, after):
        path = self.root / "template.properties"
        path.write_text(path.read_text().replace(before, after), encoding="utf-8")

    def test_valid_config_and_matching_tag(self):
        config = validate(self.root)
        validate(self.root, "v" + config["module.versionName"])

    def test_wrong_tag_is_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.root, "not-a-version")

    def test_bad_package_and_version_are_rejected(self):
        self.change("hook.targetPackage=com.example.xposed.demo", "hook.targetPackage=android")
        with self.assertRaises(ValueError):
            validate(self.root)
        self.change("hook.targetPackage=android", "hook.targetPackage=com.example.xposed.demo")
        self.change("module.versionCode=1", "module.versionCode=0")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_stale_source_entry_is_rejected(self):
        path = self.root / "app/src/main/assets/xposed_init"
        path.parent.mkdir(parents=True)
        path.write_text("OldEntry")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_source_switch_is_reversible_and_keeps_checksum(self):
        wrapper = self.root / "gradle/wrapper/gradle-wrapper.properties"
        configure(self.root, "china")
        original = wrapper.read_bytes()
        configure(self.root, "official")
        self.assertIn("services.gradle.org/distributions", wrapper.read_text())
        self.assertIn("distributionSha256Sum=", wrapper.read_text())
        configure(self.root, "china")
        self.assertEqual(original, wrapper.read_bytes())

    def apk(self, classes, entry=ENTRY):
        path = self.root / "test.apk"
        with zipfile.ZipFile(path, "w") as apk:
            apk.writestr("assets/xposed_init", entry)
            apk.writestr("classes.dex", make_dex(classes))
        return path

    def test_apk_rejects_missing_generated_class_and_bundled_xposed(self):
        descriptor = "L" + ENTRY.replace(".", "/") + ";"
        self.assertEqual(dex_classes(make_dex([descriptor])), {descriptor})
        verify(self.apk([descriptor]))
        with self.assertRaises(ValueError):
            verify(self.apk([]))
        with self.assertRaises(ValueError):
            verify(self.apk([descriptor, "Lde/robv/android/xposed/XposedBridge;"]))
        with self.assertRaises(ValueError):
            verify(self.apk([descriptor], "WrongEntry"))


if __name__ == "__main__":
    unittest.main()
