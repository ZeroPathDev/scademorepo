#!/usr/bin/env python3
"""Build private package archives and native repository metadata, without publishing.

The generated files can be uploaded to the appropriate Nexus hosted repository.
Composer, Cargo sparse and Go fixtures can also be served by an authenticated
HTTPS static repository. Never publish these names to a public registry.
"""

import argparse
import base64
import csv
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

SOURCES = Path(__file__).parent / "packages"


def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode() if isinstance(body, str) else body)


def archive(output, source, prefix):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as tar:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                tar.add(
                    path, arcname=prefix + "/" + path.relative_to(source).as_posix()
                )


def build(output, root):
    npm = output / "npm/zeropath-rehearsal-policy-1.0.0.tgz"
    archive(npm, SOURCES / "npm", "package")
    package = json.loads((SOURCES / "npm/package.json").read_text())
    package["dist"] = {
        "tarball": root + "/npm/" + npm.name,
        "shasum": hashlib.sha1(npm.read_bytes()).hexdigest(),
        "integrity": "sha512-"
        + base64.b64encode(hashlib.sha512(npm.read_bytes()).digest()).decode(),
    }
    write(
        output / "npm/@zeropath-rehearsal/policy",
        json.dumps(
            {
                "name": package["name"],
                "dist-tags": {"latest": "1.0.0"},
                "versions": {"1.0.0": package},
            }
        ),
    )

    wheel = output / "pypi/packages/zeropath_rehearsal_policy-1.0.0-py3-none-any.whl"
    wheel.parent.mkdir(parents=True, exist_ok=True)
    info = "zeropath_rehearsal_policy-1.0.0.dist-info"
    entries = {
        "zeropath_rehearsal_policy/__init__.py": (
            SOURCES / "pypi/zeropath_rehearsal_policy/__init__.py"
        ).read_bytes(),
        info
        + "/METADATA": b"Metadata-Version: 2.1\nName: zeropath-rehearsal-policy\nVersion: 1.0.0\nRequires-Dist: urllib3==1.25.8\n",
        info
        + "/WHEEL": b"Wheel-Version: 1.0\nGenerator: rehearsal-fixture\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
    }
    record = io.StringIO()
    writer = csv.writer(record, lineterminator="\n")
    for name, contents in entries.items():
        writer.writerow(
            [
                name,
                "sha256="
                + base64.urlsafe_b64encode(hashlib.sha256(contents).digest())
                .decode()
                .rstrip("="),
                len(contents),
            ]
        )
    writer.writerow([info + "/RECORD", "", ""])
    entries[info + "/RECORD"] = record.getvalue().encode()
    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as zipped:
        for name, contents in entries.items():
            zipped.writestr(name, contents)
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    write(
        output / "pypi/simple/zeropath-rehearsal-policy/index.html",
        f'<html><a href="../../packages/{wheel.name}#sha256={digest}">{wheel.name}</a></html>',
    )

    crate = output / "cargo/crates/zeropath_rehearsal_policy/1.0.0/download"
    archive(crate, SOURCES / "cargo", "zeropath_rehearsal_policy-1.0.0")
    write(
        output / "cargo/config.json",
        json.dumps({"dl": root + "/cargo/crates", "auth-required": True}),
    )
    write(
        output / "cargo/ze/ro/zeropath_rehearsal_policy",
        json.dumps(
            {
                "name": "zeropath_rehearsal_policy",
                "vers": "1.0.0",
                "cksum": hashlib.sha256(crate.read_bytes()).hexdigest(),
                "deps": [
                    {
                        "name": "itoa",
                        "req": "=1.0.10",
                        "features": [],
                        "optional": False,
                        "default_features": True,
                        "target": None,
                        "kind": "normal",
                        "registry": None,
                    }
                ],
                "features": {},
                "yanked": False,
            }
        )
        + "\n",
    )

    composer = output / "composer/dist/policy-1.0.0.zip"
    composer.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(composer, "w", zipfile.ZIP_DEFLATED) as zipped:
        for path in sorted((SOURCES / "composer").rglob("*")):
            if path.is_file():
                zipped.write(
                    path, "policy/" + path.relative_to(SOURCES / "composer").as_posix()
                )
    metadata = json.loads((SOURCES / "composer/composer.json").read_text())
    metadata["dist"] = {
        "type": "zip",
        "url": root + "/composer/dist/" + composer.name,
        "shasum": hashlib.sha1(composer.read_bytes()).hexdigest(),
    }
    write(
        output / "composer/packages.json",
        json.dumps(
            {"packages": {}, "metadata-url": root + "/composer/p2/%package%.json"}
        ),
    )
    write(
        output / "composer/p2/zeropath-rehearsal/policy.json",
        json.dumps({"packages": {metadata["name"]: [metadata]}}),
    )

    module = "example.com/zeropath/rehearsal-policy"
    version = "v1.0.0"
    go_base = output / "go" / module / "@v"
    write(go_base / "list", version + "\n")
    write(go_base / (version + ".mod"), (SOURCES / "go/go.mod").read_bytes())
    write(
        go_base / (version + ".info"),
        json.dumps({"Version": version, "Time": "2026-11-20T00:00:00Z"}),
    )
    with zipfile.ZipFile(
        go_base / (version + ".zip"), "w", zipfile.ZIP_DEFLATED
    ) as zipped:
        for path in sorted((SOURCES / "go").iterdir()):
            zipped.write(path, module + "@" + version + "/" + path.name)

    nuget = (
        output
        / "nuget/flat/zeropath.rehearsal.policy/1.0.0/zeropath.rehearsal.policy.1.0.0.nupkg"
    )
    nuget.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(nuget, "w", zipfile.ZIP_DEFLATED) as zipped:
        zipped.write(
            SOURCES / "nuget/ZeroPath.Rehearsal.Policy.nuspec",
            "ZeroPath.Rehearsal.Policy.nuspec",
        )
        zipped.write(SOURCES / "nuget/Policy.cs", "contentFiles/cs/any/Policy.cs")
        zipped.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="nuspec" ContentType="application/octet"/><Default Extension="cs" ContentType="application/octet"/></Types>',
        )
    write(
        nuget.with_suffix(".nuspec"),
        (SOURCES / "nuget/ZeroPath.Rehearsal.Policy.nuspec").read_bytes(),
    )
    write(
        output / "nuget/flat/zeropath.rehearsal.policy/index.json",
        json.dumps({"versions": ["1.0.0"]}),
    )
    write(
        output / "nuget/index.json",
        json.dumps(
            {
                "version": "3.0.0",
                "resources": [
                    {"@id": root + "/nuget/flat/", "@type": "PackageBaseAddress/3.0.0"}
                ],
            }
        ),
    )

    with tempfile.TemporaryDirectory(prefix="rehearsal-gem-") as temporary:
        # RubyGems owns the gem archive format. Missing gem is a failed fixture build.
        gem = Path(temporary) / "zeropath-rehearsal-policy-1.0.0.gem"
        subprocess.run(
            ["gem", "build", "zeropath-rehearsal-policy.gemspec", "--output", str(gem)],
            cwd=SOURCES / "rubygems",
            check=True,
        )
        write(output / "rubygems/gems" / gem.name, gem.read_bytes())
    write(
        output / "rubygems/api/v1/gems/zeropath-rehearsal-policy.json",
        json.dumps(
            {
                "name": "zeropath-rehearsal-policy",
                "version": "1.0.0",
                "dependencies": {
                    "runtime": [{"name": "rack", "requirements": "= 2.0.8"}]
                },
            }
        ),
    )

    files = [p for p in output.rglob("*") if p.is_file() and p.name != "checksums.json"]
    write(
        output / "checksums.json",
        json.dumps(
            {
                p.relative_to(output).as_posix(): hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
                for p in sorted(files)
            },
            indent=2,
        ),
    )
    print(f"Built {len(files)} files in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--base-url",
        required=True,
        help="HTTPS repository base for generated download URLs",
    )
    args = parser.parse_args()
    parsed = urlsplit(args.base_url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.query
        or parsed.fragment
    ):
        parser.error("--base-url must be HTTPS without credentials, query or fragment")
    build(args.output, args.base_url.rstrip("/"))
