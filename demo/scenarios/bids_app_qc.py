"""
BIDS demo — neuroimaging layout + BIDS-App-style QC path.

Mirrors community practice (BIDS Apps / MRIQC tutorials):
  validate/index a BIDS dataset → run a containerised app over that root.

Full fMRIPrep is intentionally not run here (hours + large images).
This demo proves the *contract*: BIDS HTTP index + task execution.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo"))

from lib.http import DemoError, request_json, require_ok, wait_health, write_report  # noqa: E402


def run(base_url: str, bids_root: Path) -> dict:
    base = base_url.rstrip("/")
    health = wait_health(base)
    adapters = health.get("adapters") or []
    if "bids" not in adapters:
        raise DemoError(f"adapter-bids not enabled; adapters={adapters}")

    # 0) Local fixture sanity (what a lab would validate with bids-validator)
    dd_path = bids_root / "dataset_description.json"
    parts_path = bids_root / "participants.tsv"
    if not dd_path.is_file() or not parts_path.is_file():
        raise DemoError(f"BIDS fixture incomplete under {bids_root}")
    local_dd = json.loads(dd_path.read_text(encoding="utf-8"))
    local_subjects = [
        line.split("\t")[0]
        for line in parts_path.read_text(encoding="utf-8").splitlines()[1:]
        if line.strip()
    ]

    # 1) HTTP index — what Synaptic Core exposes for discovery
    status, dd = request_json("GET", f"{base}/bids/dataset_description")
    dd = require_ok(status, dd, "BIDS dataset_description")
    if not dd.get("BIDSVersion"):
        raise DemoError("missing BIDSVersion")
    if not dd.get("Name"):
        raise DemoError("missing Name")

    status, parts = request_json("GET", f"{base}/bids/participants")
    parts = require_ok(status, parts, "BIDS participants")
    if "schema" not in parts or "participants" not in parts:
        raise DemoError("participants envelope missing schema/participants")

    status, deriv = request_json("GET", f"{base}/bids/derivatives")
    deriv = require_ok(status, deriv, "BIDS derivatives")

    # 2) BIDS-App-style QC summary task (MRIQC analogy)
    #    Command prints a JSON QC stub — proves container execution over BIDS metadata.
    qc_cmd = (
        "echo '{\"app\":\"sc-demo-bids-qc\",\"subjects\":"
        + json.dumps(local_subjects)
        + ",\"bids_version\":\""
        + str(local_dd.get("BIDSVersion"))
        + "\"}'"
    )
    status, task = request_json(
        "POST",
        f"{base}/ga4gh/tes/v1/tasks",
        {
            "name": "demo-bids-qc",
            "executors": [
                {
                    "image": "busybox:1.36",
                    "command": ["sh", "-c", qc_cmd],
                }
            ],
            "tags": {
                "bids_app": "sc-demo-bids-qc",
                "dataset": str(local_dd.get("Name")),
            },
        },
    )
    if status in (404, 501):
        raise DemoError(
            "TES route missing — build Core with adapter-ga4gh for BIDS-App step"
        )
    task = require_ok(status, task, "BIDS QC task", ok={200, 201})
    task_id = task.get("id")

    status, task_get = request_json("GET", f"{base}/ga4gh/tes/v1/tasks/{task_id}")
    task_get = require_ok(status, task_get, "BIDS QC task get")

    return {
        "demo": "bids_app_qc",
        "story": "BIDS index → BIDS-App-style QC task",
        "local_fixture": str(bids_root),
        "local_subjects": local_subjects,
        "http_bids_version": dd.get("BIDSVersion"),
        "http_name": dd.get("Name"),
        "participants_count": len(parts.get("participants") or []),
        "derivatives_keys": sorted(
            k for k in deriv.keys() if k in ("derivatives", "pipeline_description")
        ),
        "qc_task_id": task_id,
        "qc_state": task_get.get("state"),
        "ok": True,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default="http://127.0.0.1:8080")
    p.add_argument(
        "--bids-root",
        default=str(ROOT / "fixtures" / "bids" / "minimal"),
    )
    p.add_argument("--out", default="artifacts/bids.json")
    args = p.parse_args()
    try:
        report = run(args.base_url, Path(args.bids_root))
    except DemoError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    write_report(args.out, report)
    print(f"PASS bids — subjects {report['local_subjects']} task {report['qc_task_id']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
