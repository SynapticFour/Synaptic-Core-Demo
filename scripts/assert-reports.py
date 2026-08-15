"""Fail-closed checks on demo JSON reports (CI after live smoke)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_COMPLETE = {
    "ga4gh.json": ("wes_state", "tes_state"),
    "stac.json": ("process_state",),
    "bids.json": ("qc_state",),
}


def check_report(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("ok") is not True:
        errors.append(f"{path}: ok is not true")
    keys = REQUIRED_COMPLETE.get(path.name)
    if keys:
        for key in keys:
            if data.get(key) != "COMPLETE":
                errors.append(f"{path}: {key}={data.get(key)!r} (want COMPLETE)")
    if path.name == "stac.json" and data.get("live_catalog_backing") != "ObjectsService":
        errors.append(
            f"{path}: live_catalog_backing={data.get('live_catalog_backing')!r} "
            "(want ObjectsService)"
        )
    if path.name == "bids.json" and data.get("http_participants_backing") != "ObjectsService":
        errors.append(
            f"{path}: http_participants_backing={data.get('http_participants_backing')!r} "
            "(want ObjectsService)"
        )
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: assert-reports.py artifacts/*.json", file=sys.stderr)
        return 2
    errors: list[str] = []
    for raw in argv[1:]:
        errors.extend(check_report(Path(raw)))
    if errors:
        print("FAIL report contract:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print("OK report contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
