#!/usr/bin/env python3
"""Build real private JVM packages; optionally publish to rehearsal repositories.

Build: python3 registry-fixtures/publish.py --output /tmp/registry-fixtures
Publish adds --publish and requires REHEARSAL_MAVEN_URL, REHEARSAL_IVY_URL,
REHEARSAL_REGISTRY_USERNAME and REHEARSAL_REGISTRY_PASSWORD in the environment.
The Maven URL is a hosted repository for uploads; scanners use its Nexus group.
"""

import argparse
import base64
import hashlib
import os
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build(output: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    sources = Path(__file__).parent / "java"
    for repository, module, class_name in (
        ("maven", "maven-policy", "MavenPolicy"),
        ("ivy", "native-policy", "NativePolicy"),
    ):
        relative = (
            Path("com/zeropath/rehearsal") / module / "1.0.0"
            if repository == "maven"
            else Path("com.zeropath.rehearsal") / module / "1.0.0"
        )
        directory = output / repository / relative
        directory.mkdir(parents=True, exist_ok=True)
        jar = directory / (
            f"{module}-1.0.0.jar" if repository == "maven" else f"{module}.jar"
        )
        with tempfile.TemporaryDirectory(prefix="rehearsal-jvm-") as temp:
            subprocess.run(
                [
                    "javac",
                    "--release",
                    "11",
                    "-d",
                    temp,
                    str(sources / "com/zeropath/rehearsal" / f"{class_name}.java"),
                ],
                check=True,
            )
            with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n\n")
                for compiled in sorted(Path(temp).rglob("*.class")):
                    archive.write(compiled, compiled.relative_to(temp))
        if repository == "maven":
            descriptor = directory / f"{module}-1.0.0.pom"
            descriptor.write_text(f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.zeropath.rehearsal</groupId><artifactId>{module}</artifactId><version>1.0.0</version>
  <dependencies><dependency><groupId>commons-collections</groupId>
    <artifactId>commons-collections</artifactId><version>3.2.1</version>
  </dependency></dependencies>
</project>
""")
        else:
            descriptor = directory / "ivy.xml"
            descriptor.write_text(f'''<ivy-module version="2.0">
  <info organisation="com.zeropath.rehearsal" module="{module}" revision="1.0.0"/>
  <publications><artifact name="{module}" type="jar" ext="jar"/></publications>
  <dependencies><dependency org="commons-collections" name="commons-collections" rev="3.2.1"/></dependencies>
</ivy-module>
''')
        for artifact in (descriptor, jar):
            files.append((repository, artifact))
            for algorithm in ("sha1", "sha256", "sha512"):
                checksum = artifact.with_name(artifact.name + "." + algorithm)
                checksum.write_text(
                    hashlib.new(algorithm, artifact.read_bytes()).hexdigest() + "\n"
                )
                files.append((repository, checksum))
    return files


def publish(output: Path, files: list[tuple[str, Path]]) -> None:
    roots = {
        name: os.environ[f"REHEARSAL_{name.upper()}_URL"].rstrip("/")
        for name in ("maven", "ivy")
    }
    for url in roots.values():
        parsed = urllib.parse.urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "Rehearsal repositories require HTTPS URLs without credentials, queries or fragments"
            )
    username, password = (
        os.environ["REHEARSAL_REGISTRY_USERNAME"],
        os.environ["REHEARSAL_REGISTRY_PASSWORD"],
    )
    if not username or not password:
        raise ValueError("Rehearsal publication requires nonempty credentials")
    authorization = (
        "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
    )
    opener = urllib.request.build_opener(NoRedirect())
    for repository, path in files:
        relative = path.relative_to(output / repository).as_posix()
        url = roots[repository] + "/" + urllib.parse.quote(relative, safe="/")
        # Prove this is an authenticated fixture; public proxy-only rehearsals
        # cannot establish that internal package credentials work.
        try:
            with opener.open(
                urllib.request.Request(url, method="HEAD"), timeout=30
            ) as response:
                raise RuntimeError(
                    f"{repository} permits anonymous reads; disable anonymous access for the fixture"
                )
        except urllib.error.HTTPError as error:
            if error.code not in (401, 403, 404):
                raise RuntimeError(
                    f"{repository} anonymous probe returned HTTP {error.code}"
                ) from None
        request = urllib.request.Request(
            url,
            data=path.read_bytes(),
            method="PUT",
            headers={"Authorization": authorization},
        )
        try:
            with opener.open(request, timeout=30) as response:
                if response.status not in (200, 201, 204):
                    raise RuntimeError(
                        f"{repository} upload returned HTTP {response.status}"
                    )
            with opener.open(
                urllib.request.Request(url, headers={"Authorization": authorization}),
                timeout=30,
            ) as response:
                if response.read(len(path.read_bytes()) + 1) != path.read_bytes():
                    raise RuntimeError(
                        f"{repository} download did not match the uploaded artifact"
                    )
            try:
                with opener.open(url, timeout=30):
                    raise RuntimeError(
                        f"{repository} exposes the published fixture anonymously"
                    )
            except urllib.error.HTTPError as error:
                if error.code not in (401, 403, 404):
                    raise RuntimeError(
                        f"{repository} anonymous probe returned HTTP {error.code}"
                    ) from None
        except urllib.error.HTTPError as error:
            raise RuntimeError(
                f"{repository} publication failed with HTTP {error.code}"
            ) from None
        print(f"Verified {repository}/{relative}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    files = build(args.output)
    if args.publish:
        publish(args.output, files)
    print(f"Built {len(files)} fixture artifacts in {args.output}")


if __name__ == "__main__":
    main()
