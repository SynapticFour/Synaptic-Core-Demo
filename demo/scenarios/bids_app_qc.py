"""
BIDS laptop smoke — ingest fixture metadata, then assert live HTTP index.

The on-disk fixture is the *source* of subject/age/sex. Core's default
`/bids/dataset_description` is a DemoStore fixture (different Name). After
ingest, `/bids/participants` must flip to ObjectsService with the fixture's
subject row. QC compute is busybox echo, not MRIQC/fMRIPrep.
"""

from __future__ import annotations

import argparse
import json
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


def _load_participants(tsv: Path) -> list[dict[str, str]]:
    lines = [ln for ln in tsv.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) < 2:
        raise DemoError(f"no participant rows in {tsv}")
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        cols = line.split("\t")
        rows.append({header[i]: cols[i] for i in range(min(len(header), len(cols)))})
    return rows


def run(base_url: str, bids_root: str) -> dict:
    base = base_url.rstrip("/")
    bids_root_p = Path(bids_root)
    wait_health(base)

    dd_path = bids_root_p / "dataset_description.json"
    parts_path = bids_root_p / "participants.tsv"
    nii_path = bids_root_p / "sub-01" / "anat" / "sub-01_T1w.nii.gz"
    if not dd_path.is_file() or not parts_path.is_file() or not nii_path.is_file():
        raise DemoError(f"BIDS fixture incomplete under {bids_root_p}")
    local_dd = json.loads(dd_path.read_text(encoding="utf-8"))
    local_rows = _load_participants(parts_path)
    subject = local_rows[0].get("participant_id") or ""
    age_s = local_rows[0].get("age") or ""
    sex = local_rows[0].get("sex") or ""
    try:
        age = int(age_s)
    except ValueError as e:
        raise DemoError(f"fixture age not int: {age_s!r}") from e
    nii_bytes = list(nii_path.read_bytes())

    status, dd_before = request_json("GET", f"{base}/bids/dataset_description")
    dd_before = require_ok(status, dd_before, "BIDS dataset_description")
    if dd_before.get("demo") is not True:
        raise DemoError(
            "dataset_description must remain a Core fixture (demo=true); "
            f"got {dd_before}"
        )
    if dd_before.get("Name") == local_dd.get("Name"):
        raise DemoError(
            "HTTP dataset_description Name unexpectedly equals the on-disk fixture — "
            "this demo asserts they are different until Core projects layout files"
        )

    status, ingested = request_json(
        "POST",
        f"{base}/sc/objects/v1/ingest",
        {
            "name": "sub-01_T1w.nii.gz",
            "bytes": nii_bytes,
            "mime_type": "application/gzip",
            "metadata": {
                "subject": subject,
                "modality": "anat",
                "task": "rest",
                "age": age,
                "sex": sex,
            },
            "is_encrypted": False,
        },
    )
    ingested = require_ok(status, ingested, "BIDS ingest", ok={200, 201})
    object_id = extract_id(ingested, "id")

    status, parts = request_json("GET", f"{base}/bids/participants")
    parts = require_ok(status, parts, "BIDS participants")
    if parts.get("backing") != "ObjectsService" or parts.get("demo") is not False:
        raise DemoError(
            "after ingest expected live ObjectsService participants, "
            f"got backing={parts.get('backing')!r} demo={parts.get('demo')!r}"
        )
    live_rows = parts.get("participants") or []
    match = next((p for p in live_rows if p.get("participant_id") == subject), None)
    if match is None:
        raise DemoError(f"ingested subject {subject} missing from HTTP participants: {live_rows}")
    if match.get("age") != age or match.get("sex") != sex:
        raise DemoError(
            f"live participant {match} does not match fixture age={age} sex={sex}"
        )
    live_oid = match.get("object_id")
    if live_oid is None:
        raise DemoError(f"live participant missing object_id: {match}")
    live_oid_s = live_oid if isinstance(live_oid, str) else extract_id(live_oid)
    if live_oid_s != object_id:
        raise DemoError(f"participant object_id {live_oid_s} != ingest {object_id}")

    status, deriv = request_json("GET", f"{base}/bids/derivatives")
    deriv = require_ok(status, deriv, "BIDS derivatives")

    qc_cmd = (
        "echo '{\"app\":\"sc-demo-bids-qc\",\"subject\":"
        + json.dumps(subject)
        + ",\"object_id\":"
        + json.dumps(object_id)
        + "}'"
    )
    status, task = request_json(
        "POST",
        f"{base}/ga4gh/tes/v1/tasks",
        {
            "name": "demo-bids-qc",
            "executors": [
                {
                    "image": DEMO_CONTAINER_IMAGE,
                    "command": ["sh", "-c", qc_cmd],
                }
            ],
            "tags": {
                "bids_app": "sc-demo-bids-qc-echo",
                "dataset": str(local_dd.get("Name")),
                "object_id": object_id,
            },
        },
    )
    if status in (404, 501):
        raise DemoError("TES route missing — build Core with adapter-ga4gh")
    task = require_ok(status, task, "BIDS QC task", ok={200, 201})
    task_id = extract_id(task, "id")
    tes = poll_until_complete(f"{base}/ga4gh/tes/v1/tasks/{task_id}", "BIDS QC TES")
    require_complete(tes.get("state"), "BIDS QC TES")

    return {
        "demo": "bids_app_qc",
        "claim": "fixture TSV ingested; /bids/participants is ObjectsService with same subject/age/sex; TES COMPLETE",
        "not_claimed": "MRIQC/fMRIPrep/bids-validator as Core",
        "local_fixture": str(
            bids_root_p.resolve().relative_to(ROOT)
            if bids_root_p.resolve().is_relative_to(ROOT)
            else bids_root_p
        ),
        "local_name": local_dd.get("Name"),
        "local_subject": subject,
        "http_dataset_name": dd_before.get("Name"),
        "http_dataset_demo": True,
        "http_participants_backing": parts.get("backing"),
        "http_participants_demo": parts.get("demo"),
        "live_age": match.get("age"),
        "live_sex": match.get("sex"),
        "object_id": object_id,
        "derivatives_keys": sorted(
            k for k in deriv.keys() if k in ("derivatives", "pipeline_description", "backing", "demo")
        ),
        "qc_task_id": task_id,
        "qc_state": tes.get("state"),
        "ok": True,
    }


if __name__ == "__main__":
    def extra(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--bids-root",
            default=str(ROOT / "fixtures" / "bids" / "minimal"),
        )

    raise SystemExit(
        run_main(
            __doc__ or "BIDS demo",
            "artifacts/bids.json",
            run,
            extra_args=extra,
        )
    )
