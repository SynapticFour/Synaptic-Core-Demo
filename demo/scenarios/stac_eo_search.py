"""
STAC laptop smoke — fixture catalogue, then live ObjectsService projection.

Seeded `demo-eo` / `demo-item-1` is a Core fixture (example.com thumbnail).
This demo also ingests a STAC Feature so search can prove live backing.
Compute is busybox echo; not NDVI / stackstac.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo"))

from lib.http import (  # noqa: E402
    DemoError,
    extract_id,
    poll_until_complete,
    request_json,
    require_complete,
    require_ok,
    wait_health,
)
from lib.runner import DEMO_CONTAINER_IMAGE, run_main  # noqa: E402

LIVE_COLLECTION = "sc-demo-live"


def run(base_url: str) -> dict:
    base = base_url.rstrip("/")
    wait_health(base)

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

    status, cols = request_json("GET", f"{base}/stac/collections")
    cols = require_ok(status, cols, "STAC collections")
    col_ids = [c.get("id") for c in (cols.get("collections") or [])]
    if "demo-eo" not in col_ids:
        raise DemoError(f"demo-eo collection missing before ingest; have {col_ids}")

    fixture_backing = root.get("synaptic:backing")
    fixture_demo = bool(root.get("demo"))

    search_fixture = {
        "collections": ["demo-eo"],
        "bbox": [13.0, 52.3, 13.6, 52.7],
        "datetime": "2020-01-01T00:00:00Z/2030-12-31T23:59:59Z",
        "limit": 10,
    }
    status, fc = request_json("POST", f"{base}/stac/search", search_fixture)
    fc = require_ok(status, fc, "STAC fixture search")
    features = fc.get("features") or []
    fixture_item = next((f for f in features if f.get("id") == "demo-item-1"), None)
    fixture_thumb = None
    if fixture_item:
        href = ((fixture_item.get("assets") or {}).get("thumbnail") or {}).get("href")
        fixture_thumb = href
        if href and "example.com" not in href:
            raise DemoError(
                f"fixture demo-item-1 thumbnail was expected to be example.com, got {href}"
            )

    live_meta = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "collection": LIVE_COLLECTION,
        "id": "sc-demo-live-1",
        "geometry": {"type": "Point", "coordinates": [13.405, 52.52]},
        "bbox": [13.4, 52.51, 13.41, 52.53],
        "properties": {
            "datetime": "2026-08-15T00:00:00Z",
            "title": "ingested Core demo scene",
        },
    }
    status, ingested = request_json(
        "POST",
        f"{base}/sc/objects/v1/ingest",
        {
            "name": "sc-demo-live-1.bin",
            "bytes": list(b"stac-live-payload"),
            "mime_type": "application/octet-stream",
            "metadata": live_meta,
            "is_encrypted": False,
        },
    )
    ingested = require_ok(status, ingested, "STAC ingest", ok={200, 201})
    live_object_id = extract_id(ingested, "id")

    status, root2 = request_json("GET", f"{base}/stac")
    root2 = require_ok(status, root2, "STAC root after ingest")
    live_backing = root2.get("synaptic:backing")
    if live_backing != "ObjectsService":
        raise DemoError(
            f"after STAC ingest expected synaptic:backing=ObjectsService, got {live_backing!r}"
        )

    status, live_fc = request_json(
        "POST",
        f"{base}/stac/search",
        {
            "collections": [LIVE_COLLECTION],
            "bbox": [13.0, 52.3, 13.6, 52.7],
            "limit": 10,
        },
    )
    live_fc = require_ok(status, live_fc, "STAC live search")
    live_features = live_fc.get("features") or []
    live_item = next(
        (
            f
            for f in live_features
            if f.get("id") in {"sc-demo-live-1", live_object_id}
            or f.get("collection") == LIVE_COLLECTION
        ),
        None,
    )
    if live_item is None:
        raise DemoError(f"live collection {LIVE_COLLECTION} missing from search: {live_features}")
    assets = live_item.get("assets") or {}
    any_stream = any(
        "/sc/objects/" in str((a or {}).get("href") or "")
        or live_object_id in str((a or {}).get("href") or "")
        for a in assets.values()
        if isinstance(a, dict)
    )
    if not any_stream:
        raise DemoError(f"live STAC item has no ObjectsService asset href: {assets}")

    status, task = request_json(
        "POST",
        f"{base}/ga4gh/tes/v1/tasks",
        {
            "name": "demo-eo-echo",
            "executors": [
                {
                    "image": DEMO_CONTAINER_IMAGE,
                    "command": [
                        "sh",
                        "-c",
                        f"echo stac-live={live_item.get('id')}",
                    ],
                }
            ],
            "tags": {"collection": LIVE_COLLECTION, "kind": "echo-stand-in"},
        },
    )
    if status in (404, 501):
        raise DemoError("TES route missing — build Core with adapter-ga4gh")
    task = require_ok(status, task, "EO process task", ok={200, 201})
    task_id = extract_id(task, "id")
    tes = poll_until_complete(f"{base}/ga4gh/tes/v1/tasks/{task_id}", "EO TES")
    require_complete(tes.get("state"), "EO TES")

    return {
        "demo": "stac_eo_search",
        "claim": "fixture search distinguished from live ObjectsService STAC projection; TES COMPLETE",
        "not_claimed": "NDVI/stackstac/Planetary Computer",
        "fixture_collection": "demo-eo",
        "fixture_item_id": (fixture_item or {}).get("id"),
        "fixture_thumbnail": fixture_thumb,
        "fixture_catalog_backing": fixture_backing,
        "fixture_catalog_demo": fixture_demo,
        "live_collection": LIVE_COLLECTION,
        "live_object_id": live_object_id,
        "live_item_id": live_item.get("id"),
        "live_catalog_backing": live_backing,
        "process_task_id": task_id,
        "process_state": tes.get("state"),
        "ok": True,
    }


if __name__ == "__main__":
    raise SystemExit(
        run_main(
            __doc__ or "STAC demo",
            "artifacts/stac.json",
            run,
        )
    )
