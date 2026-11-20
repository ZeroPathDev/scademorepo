"""Build real private artifacts and validate the explicit rehearsal contract."""

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import build_packages
import publish

ROOT = Path(__file__).resolve().parents[1]


class FixtureTests(unittest.TestCase):
    def test_canary_contract(self):
        corpus = json.loads(
            (ROOT / "registry-fixtures/native-canaries.json").read_text()
        )
        self.assertEqual(corpus["schemaVersion"], 1)
        self.assertEqual(
            {c["ecosystem"] for c in corpus["canaries"]},
            {
                "ivy",
                "npm",
                "python",
                "cargo",
                "bundler",
                "composer",
                "dotnet",
                "go",
                "sbt",
            },
        )
        self.assertEqual(
            len({c["manifest"] for c in corpus["canaries"]}), len(corpus["canaries"])
        )
        for canary in corpus["canaries"]:
            self.assertIn(canary["manifest"], canary["files"])
            for relative in canary["files"]:
                self.assertTrue((ROOT / relative).is_file(), relative)
                self.assertTrue((ROOT / relative).resolve().is_relative_to(ROOT))
            self.assertTrue(
                any("rehearsal" in name.lower() for name, _ in canary["expected"])
            )
            self.assertTrue(
                any("rehearsal" not in name.lower() for name, _ in canary["expected"])
            )
        expected = json.loads(
            (ROOT / "registry-fixtures/expected-ivy-inventory.json").read_text()
        )
        self.assertEqual(len(expected["manifests"]), 8)
        self.assertFalse(
            expected["manifests"]["ivy-partial-resolution/ivy.xml"]["complete"]
        )
        for manifest, result in expected["manifests"].items():
            self.assertTrue((ROOT / manifest).is_file(), manifest)
            self.assertEqual(result["requiresCoverageWarning"], not result["complete"])
            known = {
                (package["name"], package["version"])
                for package in result["minimumPackages"]
            }
            for edge in result["minimumEdges"]:
                self.assertIn(tuple(edge["parent"]), known)
                self.assertIn(tuple(edge["child"]), known)
        for app in ("ivy-public-default", "ivy-private-maven", "ivy-private-native"):
            self.assertFalse((ROOT / app / "ivysettings.xml").exists())

    def test_jvm_bytecode_and_checksums(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            files = publish.build(output)
            self.assertEqual(len(files), 16)
            for _, path in files:
                if path.suffix in {".sha1", ".sha256", ".sha512"}:
                    self.assertEqual(
                        path.read_text().strip(),
                        hashlib.new(
                            path.suffix[1:], path.with_suffix("").read_bytes()
                        ).hexdigest(),
                    )
                if path.suffix == ".jar":
                    with zipfile.ZipFile(path) as archive:
                        classes = [
                            name
                            for name in archive.namelist()
                            if name.endswith(".class")
                        ]
                        self.assertEqual(len(classes), 1)
                        self.assertEqual(
                            archive.read(classes[0])[:4], bytes.fromhex("cafebabe")
                        )
            self.assertFalse(list((output / "ivy").rglob("*.pom")))

    def test_native_archives(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            build_packages.build(output, "https://rehearsal.invalid")
            checksums = json.loads((output / "checksums.json").read_text())
            self.assertEqual(
                set(checksums),
                {
                    p.relative_to(output).as_posix()
                    for p in output.rglob("*")
                    if p.is_file() and p.name != "checksums.json"
                },
            )
            for relative, expected in checksums.items():
                self.assertEqual(
                    hashlib.sha256((output / relative).read_bytes()).hexdigest(),
                    expected,
                )
            with zipfile.ZipFile(next(output.rglob("*.whl"))) as wheel:
                self.assertIn(
                    b"Requires-Dist: urllib3==1.25.8",
                    wheel.read("zeropath_rehearsal_policy-1.0.0.dist-info/METADATA"),
                )
                self.assertIn("zeropath_rehearsal_policy/__init__.py", wheel.namelist())
            with zipfile.ZipFile(next(output.rglob("*.nupkg"))) as package:
                self.assertIn("contentFiles/cs/any/Policy.cs", package.namelist())
                self.assertIn(
                    b"Newtonsoft.Json", package.read("ZeroPath.Rehearsal.Policy.nuspec")
                )
            cargo = json.loads(
                (output / "cargo/ze/ro/zeropath_rehearsal_policy").read_text()
            )
            self.assertEqual(cargo["deps"][0]["name"], "itoa")
            self.assertEqual(
                cargo["cksum"],
                checksums["cargo/crates/zeropath_rehearsal_policy/1.0.0/download"],
            )


if __name__ == "__main__":
    unittest.main()
