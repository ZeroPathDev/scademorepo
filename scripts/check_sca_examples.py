"""Recheck the recorded SCA inventory against OSV using Python's standard library."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
OSV_URL = "https://api.osv.dev/v1/querybatch"
FIXTURES = {
    f"{ecosystem}-{status}"
    for ecosystem in ("maven", "npm", "pypi", "cpp")
    for status in ("vulnerable", "clean")
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def query_osv(packages):
    pending = [(i, package["osv_query"]) for i, package in enumerate(packages)]
    findings = [set() for _ in packages]
    while pending:
        request = urllib.request.Request(
            OSV_URL,
            data=json.dumps({"queries": [query for _, query in pending]}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            results = json.load(response)["results"]
        check(len(results) == len(pending), "OSV returned an incomplete response")
        next_page = []
        for (index, query), result in zip(pending, results):
            check("error" not in result, f"OSV query failed: {result}")
            findings[index].update(v["id"] for v in result.get("vulns", []))
            if result.get("next_page_token"):
                next_page.append(
                    (index, {**query, "page_token": result["next_page_token"]})
                )
        pending = next_page
    for package, advisories in zip(packages, findings):
        package["advisory_ids"] = sorted(advisories)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the refreshed audit report")
    args = parser.parse_args()
    report = json.loads((ROOT / "sca-audit.json").read_text(encoding="utf-8"))
    check(report["schema_version"] == 1, "Unsupported audit report version")
    fixtures = report["fixtures"]
    check(set(fixtures) == FIXTURES, "Expected exactly one pair per ecosystem")
    packages = []
    for name, fixture in fixtures.items():
        check(fixture["input_sha256"], f"{name}: missing input fingerprints")
        for filename, expected in fixture["input_sha256"].items():
            # Universal newline handling keeps hashes stable across Git checkouts.
            content = (ROOT / name / filename).read_text(encoding="utf-8").encode()
            actual = hashlib.sha256(content).hexdigest()
            check(actual == expected, f"{name}/{filename} changed; regenerate its inventory")
        entries = fixture["packages"]
        check(entries, f"{name}: missing package inventory")
        check(
            len({(p["name"], p["version"]) for p in entries}) == len(entries),
            f"{name}: duplicate package inventory entries",
        )
        check(
            {p["relationship"] for p in entries} == {"direct", "transitive"},
            f"{name}: expected both direct and transitive dependencies",
        )
        packages.extend(entries)

    query_osv(packages)
    passed = True
    for name, fixture in fixtures.items():
        entries = fixture["packages"]
        direct = sum(p["relationship"] == "direct" for p in entries)
        vulnerable = sum(bool(p["advisory_ids"]) for p in entries)
        ok = vulnerable == 0 if name.endswith("-clean") else vulnerable >= 2
        fixture["vulnerable_package_count"] = vulnerable
        fixture["passed"] = ok
        passed = passed and ok
        print(
            f"{'PASS' if ok else 'FAIL'} {name}: {direct} direct, "
            f"{len(entries) - direct} transitive, {vulnerable} vulnerable packages"
        )
    report["checked_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError) as error:
        print(f"Audit failed: {error}", file=sys.stderr)
        sys.exit(2)
