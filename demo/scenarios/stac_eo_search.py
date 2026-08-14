"""
STAC demo — Earth observation catalogue path.

Mirrors common EO tutorials (Element84 Earth Search, Planetary Computer):
  landing → search by bbox/datetime → fetch Item → enqueue a process task.

Real-world analogues: Sentinel-2 / Landsat STAC search then cloud-native process.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo"))

from lib.http import DemoError, request_json, require_ok, wait_health, write_report  # noqa: E402


def run(base_url: str) -> dict:
    base = base_url.rstrip("/")
    health = wait_health(base)
    adapters = health.get("adapters") or []
    if "stac" not in adapters:
        raise DemoError(f"adapter-stac not enabled; adapters={adapters}")

    # 1) Landing / conformance (STAC API Core)
    status, root = request_json("GET", f"{base}/stac")
    root = require_ok(status, root, "STAC root")
    if root.get("type") != "Catalog":
        raise DemoError(f"expected Catalog, got {root.get('type')}")
    conforms = root.get("conformsTo") or []
    for needed in (
        "https://api.stacspec.org/v1.0.0/core",
        "https://api.stacspec.org/v1.0.0/item-search",
    ):
        if needed not in conforms:
            raise DemoError(f"missing conformsTo {needed}")

    # 2) Collections — seeded demo-eo (like a local Sentinel collection)
    status, cols = request_json("GET", f"{base}/stac/collections")
    cols = require_ok(status, cols, "STAC collections")
    ids = [c.get("id") for c in (cols.get("collections") or [])]
    if "demo-eo" not in ids:
        raise DemoError(f"demo-eo collection missing; have {ids}")

    # 3) Item Search — Berlin-ish bbox / time window (tutorial style)
    search_body = {
        "collections": ["demo-eo"],
        "bbox": [13.0, 52.3, 13.6, 52.7],
        "datetime": "2020-01-01T00:00:00Z/2030-12-31T23:59:59Z",
        "limit": 10,
    }
    status, fc = request_json("POST", f"{base}/stac/search", search_body)
    fc = require_ok(status, fc, "STAC search")
    if fc.get("type") != "FeatureCollection":
        raise DemoError("search did not return FeatureCollection")
    features = fc.get("features") or []
    if not features:
        raise DemoError("search returned no features for demo-eo")
    item = features[0]
    item_id = item.get("id")
    assets = item.get("assets") or {}

    # 4) Fetch item by id
    status, item2 = request_json(
        "GET", f"{base}/stac/collections/demo-eo/items/{item_id}"
    )
    item2 = require_ok(status, item2, "STAC item get")

    # 5) Process path — TES/task stand-in for "compute NDVI on scene"
    #    (full raster stackstac/xarray is out of scope; prove catalogue→compute)
    status, task = request_json(
        "POST",
        f"{base}/ga4gh/tes/v1/tasks",
        {
            "name": "demo-eo-scene-summary",
            "executors": [
                {
                    "image": "busybox:1.36",
                    "command": [
                        "sh",
                        "-c",
                        f"echo stac-item={item_id}; echo assets={len(assets)}",
                    ],
                }
            ],
            "tags": {"collection": "demo-eo", "item_id": item_id, "kind": "eo-summary"},
        },
    )
    # TES may be unavailable if only stac feature — but Choice A default includes ga4gh
    if status in (404, 501):
        raise DemoError(
            "TES route missing — build Core with adapter-ga4gh for EO process step"
        )
    task = require_ok(status, task, "EO process task", ok={200, 201})

    return {
        "demo": "stac_eo_search",
        "story": "STAC search → Item → process task",
        "collection": "demo-eo",
        "item_id": item_id,
        "feature_count": len(features),
        "asset_keys": sorted(assets.keys()),
        "item_datetime": (item2.get("properties") or {}).get("datetime"),
        "process_task_id": task.get("id"),
        "ok": True,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default="http://127.0.0.1:8080")
    p.add_argument("--out", default="artifacts/stac.json")
    args = p.parse_args()
    try:
        report = run(args.base_url)
    except DemoError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    write_report(args.out, report)
    print(f"PASS stac — item {report['item_id']} task {report['process_task_id']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
