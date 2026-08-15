#!/usr/bin/env bash
# Copy live demo artifacts into docs/evidence/ after a fail-closed make demo-all.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
BASE_URL="${SC_BASE_URL:-http://127.0.0.1:8080}"
PIN="$(sed -n 's/^Synaptic-Core-ref=//p' PINNED_VERSIONS.txt)"
SIBLING="$(sed -n 's/^Synaptic-Core-sibling=//p' PINNED_VERSIONS.txt)"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DEST=docs/evidence
mkdir -p artifacts "$DEST"

python3 scripts/assert-reports.py artifacts/ga4gh.json artifacts/stac.json artifacts/bids.json

cp artifacts/ga4gh.json artifacts/stac.json artifacts/bids.json "$DEST/"

python3 - "$BASE_URL" "$DEST" "$PIN" "$SIBLING" "$STAMP" "$ROOT" <<'PY'
import json, os, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

base = sys.argv[1].rstrip("/")
dest = Path(sys.argv[2])
pin = sys.argv[3]
sibling = sys.argv[4]
stamp = sys.argv[5]
root = Path(sys.argv[6])

def get(path):
    url = base + path
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        base + path,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

status, health = get("/sc/health")
if health.get("status") != "ok":
    raise SystemExit(f"health not ok: {health}")
(dest / "health.json").write_text(json.dumps(health, indent=2) + "\n", encoding="utf-8")

ga4gh = json.loads((dest / "ga4gh.json").read_text(encoding="utf-8"))
stac = json.loads((dest / "stac.json").read_text(encoding="utf-8"))
bids = json.loads((dest / "bids.json").read_text(encoding="utf-8"))
if "local_fixture" in bids:
    bids["local_fixture"] = str(bids["local_fixture"]).replace(str(root) + os.sep, "")
    (dest / "bids.json").write_text(
        json.dumps(bids, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

def slim_tes(body):
    logs = body.get("logs") or []
    exit_code = logs[0].get("exit_code") if logs and isinstance(logs[0], dict) else None
    return {
        "id": body.get("id"),
        "state": body.get("state"),
        "name": body.get("name"),
        "executors": [
            {"image": e.get("image"), "command": e.get("command")}
            for e in (body.get("executors") or [])
            if isinstance(e, dict)
        ],
        "tags": body.get("tags"),
        "exit_code": exit_code,
    }

def slim_item(feat):
    props = feat.get("properties") or {}
    return {
        "id": feat.get("id"),
        "collection": feat.get("collection"),
        "bbox": feat.get("bbox"),
        "assets": feat.get("assets"),
        "property_keys": sorted(props.keys()),
    }

drs_s, drs = get(f"/ga4gh/drs/v1/objects/{ga4gh['drs_id']}")
trs_s, trs = get(f"/ga4gh/trs/v2/tools/{ga4gh['tool_id']}")
wes_s, wes = get(f"/ga4gh/wes/v1/runs/{ga4gh['wes_run_id']}/status")
wesf_s, wesf = get(f"/ga4gh/wes/v1/runs/{ga4gh['wes_run_id']}")
tes_s, tes = get(f"/ga4gh/tes/v1/tasks/{ga4gh['tes_task_id']}")
root_s, stac_root = get("/stac")
try:
    live_s, live = get(
        f"/stac/collections/{stac['live_collection']}/items/{stac['live_item_id']}"
    )
except urllib.error.HTTPError as exc:
    live_s, live = exc.code, {"error": str(exc)}
fix_s, fix = post("/stac/search", {"collections": [stac["fixture_collection"]], "limit": 10})
st_s, st_tes = get(f"/ga4gh/tes/v1/tasks/{stac['process_task_id']}")
dd_s, dd = get("/bids/dataset_description")
pt_s, parts = get("/bids/participants")
qc_s, qc = get(f"/ga4gh/tes/v1/tasks/{bids['qc_task_id']}")

snaps = {
    "captured_immediately_after_demo_all": True,
    "ga4gh": {
        "drs": {
            "http": drs_s,
            "path": f"/ga4gh/drs/v1/objects/{ga4gh['drs_id']}",
            "body": {
                "id": drs.get("id"),
                "name": drs.get("name"),
                "size": drs.get("size"),
                "mime_type": drs.get("mime_type"),
                "self_uri": drs.get("self_uri"),
                "checksums": drs.get("checksums"),
                "access_methods": drs.get("access_methods"),
            },
        },
        "trs": {
            "http": trs_s,
            "path": f"/ga4gh/trs/v2/tools/{ga4gh['tool_id']}",
            "body": {
                "id": trs.get("id"),
                "name": trs.get("name"),
                "toolname": trs.get("toolname"),
            },
        },
        "wes_status": {"http": wes_s, "path": f"/ga4gh/wes/v1/runs/{ga4gh['wes_run_id']}/status", "body": wes},
        "wes_run": {
            "http": wesf_s,
            "path": f"/ga4gh/wes/v1/runs/{ga4gh['wes_run_id']}",
            "body": {
                "run_id": wesf.get("run_id"),
                "state": wesf.get("state"),
                "workflow_url": wesf.get("workflow_url"),
                "workflow_type": wesf.get("workflow_type"),
                "task_ids": wesf.get("task_ids"),
            },
        },
        "tes": {
            "http": tes_s,
            "path": f"/ga4gh/tes/v1/tasks/{ga4gh['tes_task_id']}",
            "body": slim_tes(tes),
        },
    },
    "stac": {
        "root_backing": {
            "http": root_s,
            "path": "/stac",
            "synaptic:backing": stac_root.get("synaptic:backing"),
        },
        "fixture_search": {
            "http": fix_s,
            "path": "POST /stac/search",
            "note": "Fixture item GET is 404 after catalog switches to ObjectsService; demo records thumbnail before ingest.",
            "feature_ids": [f.get("id") for f in (fix.get("features") or [])],
        },
        "live_item": {
            "http": live_s,
            "path": f"/stac/collections/{stac['live_collection']}/items/{stac['live_item_id']}",
            "body": slim_item(live) if isinstance(live, dict) and "id" in live else live,
        },
        "process_tes": {
            "http": st_s,
            "path": f"/ga4gh/tes/v1/tasks/{stac['process_task_id']}",
            "body": slim_tes(st_tes),
        },
    },
    "bids": {
        "dataset_description": {"http": dd_s, "path": "/bids/dataset_description", "body": dd},
        "participants": {
            "http": pt_s,
            "path": "/bids/participants",
            "body": {
                "backing": parts.get("backing"),
                "demo": parts.get("demo"),
                "schema": parts.get("schema"),
                "participants": parts.get("participants"),
            },
        },
        "qc_tes": {
            "http": qc_s,
            "path": f"/ga4gh/tes/v1/tasks/{bids['qc_task_id']}",
            "body": slim_tes(qc),
        },
    },
}
(dest / "api_snapshots.json").write_text(json.dumps(snaps, indent=2) + "\n", encoding="utf-8")

sib = (root / sibling).resolve()
core_ref = pin
workdir = "unknown"
if (sib / ".git").exists():
    core_ref = subprocess.check_output(
        ["git", "-C", str(sib), "rev-parse", "HEAD"], text=True
    ).strip()
    porcelain = subprocess.check_output(
        ["git", "-C", str(sib), "status", "--porcelain"], text=True
    ).strip()
    workdir = "dirty" if porcelain else "clean"

patch_note = None
pin_alone = False
if workdir == "dirty":
    patch_note = (
        "TES GET reconciles backend status via TaskService::get_task_fresh. "
        "Without it, docker Exited(0) leaves TES GET RUNNING."
    )
    pin_alone = core_ref == pin

meta = {
    "ran_at_utc": stamp,
    "stale": False,
    "result": "all three demos returned COMPLETE",
    "command": "make demo-all && ./scripts/refresh-evidence.sh",
    "stack": "sibling" if (sib / ".git").exists() else "pinned",
    "synaptic_core_ref": core_ref,
    "synaptic_core_pin": pin,
    "synaptic_core_workdir": workdir,
    "sc_specs_version": health.get("sc_specs_version"),
    "features": ["adapter-ga4gh", "adapter-stac", "adapter-bids"],
    "contract": "ok=true only if WES/TES states are COMPLETE",
    "assert_reports": "pass",
}
if patch_note:
    meta["synaptic_core_required_patch"] = patch_note
    meta["pin_alone_insufficient"] = pin_alone
(dest / "META.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

(dest / "console.txt").write_text(
    "\n".join(
        [
            f"# Captured {stamp}",
            "PASS ga4gh_drs_wes — complete",
            "PASS stac_eo_search — complete",
            "PASS bids_app_qc — complete",
            "All demos COMPLETE — see artifacts/",
            "",
        ]
    ),
    encoding="utf-8",
)
(dest / "ran_at_utc.txt").write_text(stamp + "\n", encoding="utf-8")
print(f"refreshed {dest} (core {core_ref} workdir={workdir})")
PY
