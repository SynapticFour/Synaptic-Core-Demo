"""
GA4GH laptop smoke — DRS + TRS + WES + TES against Synaptic Core.

This is not samtools, GATK, or a Dockstore workflow. Compute is a pinned
busybox echo so TES/WES lifecycle can be asserted on a laptop. The proof is
the API contract and COMPLETE, not bioinformatics.
"""

from __future__ import annotations

import sys
import time
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


def run(base_url: str) -> dict:
    base = base_url.rstrip("/")
    wait_health(base)

    payload = {
        "name": "demo-reads.fastq.txt",
        "bytes": list(b"@demo_read\nACGT\n+\nIIII\n"),
        "mime_type": "text/plain",
        "metadata": {
            "biosample_id": "demo-sample-1",
            "dataset_id": "sc-demo-ga4gh",
            "source": "synaptic-core-demo",
        },
        "is_encrypted": False,
    }
    status, body = request_json("POST", f"{base}/sc/objects/v1/ingest", payload)
    obj = require_ok(status, body, "ingest", ok={200, 201})
    object_id = extract_id(obj, "id")

    status, drs = request_json("GET", f"{base}/ga4gh/drs/v1/objects/{object_id}")
    drs = require_ok(status, drs, "DRS get")
    if not (drs.get("access_methods") or []):
        raise DemoError("DRS object has no access_methods")

    tool_name = f"sc-demo-echo-{int(time.time())}"
    status, tool = request_json(
        "POST",
        f"{base}/sc/registry/v1/tools",
        {
            "name": tool_name,
            "version": "1.0.0",
            "container_image": DEMO_CONTAINER_IMAGE,
            "description": "Laptop echo stand-in; not a genomics tool",
            "metadata": {"domain": "demo", "stand_in": True},
        },
    )
    tool = require_ok(status, tool, "register tool", ok={200, 201})
    tool_id = extract_id(tool, "id")

    status, trs_tool = request_json("GET", f"{base}/ga4gh/trs/v2/tools/{tool_id}")
    trs_tool = require_ok(status, trs_tool, "TRS get tool")
    descriptor_url = (
        f"{base}/ga4gh/trs/v2/tools/{tool_id}/versions/1.0.0/CWL/descriptor"
    )
    status, desc = request_json("GET", descriptor_url)
    desc = require_ok(status, desc, "TRS descriptor")

    # Core WES requires non-empty `steps` and stores workflow_url; it does not
    # fetch/execute the CWL file. workflow_url points at the TRS descriptor we
    # just fetched so the registered tool is actually referenced.
    wes_payload = {
        "workflow_url": descriptor_url,
        "workflow_type": "cwl",
        "workflow_params": {"input_drs_id": object_id, "trs_tool_id": tool_id},
        "steps": [
            {
                "name": "echo-stand-in",
                "container_image": DEMO_CONTAINER_IMAGE,
                "command": ["sh", "-c", "echo ga4gh-demo-ok"],
            }
        ],
    }
    status, created = request_json("POST", f"{base}/ga4gh/wes/v1/runs", wes_payload)
    created = require_ok(status, created, "WES create", ok={200, 201})
    run_id = extract_id(created, "run_id", "id")
    wes = poll_until_complete(
        f"{base}/ga4gh/wes/v1/runs/{run_id}/status",
        "WES status",
    )
    require_complete(wes.get("state"), "WES")

    tes_payload = {
        "name": "demo-tes-echo",
        "executors": [{"image": DEMO_CONTAINER_IMAGE, "command": ["echo", "tes-demo-ok"]}],
        "inputs": [{"url": f"drs://synaptic-core/{object_id}"}],
    }
    status, task = request_json("POST", f"{base}/ga4gh/tes/v1/tasks", tes_payload)
    task = require_ok(status, task, "TES create", ok={200, 201})
    task_id = extract_id(task, "id")
    tes = poll_until_complete(f"{base}/ga4gh/tes/v1/tasks/{task_id}", "TES get")
    require_complete(tes.get("state"), "TES")
    executors = tes.get("executors") or []
    if not executors or (executors[0] or {}).get("image") != DEMO_CONTAINER_IMAGE:
        raise DemoError(f"TES GET image mismatch: {tes}")

    return {
        "demo": "ga4gh_drs_wes",
        "claim": "DRS resolve + TRS register + WES/TES reach COMPLETE with echo stand-in",
        "not_claimed": "samtools/GATK/Dockstore execution",
        "object_id": object_id,
        "drs_id": drs.get("id") or object_id,
        "tool_id": tool_id,
        "trs_tool_name": trs_tool.get("name"),
        "wes_workflow_url": descriptor_url,
        "wes_run_id": run_id,
        "wes_state": wes.get("state"),
        "tes_task_id": task_id,
        "tes_state": tes.get("state"),
        "tes_image": (executors[0] or {}).get("image"),
        "ok": True,
    }


if __name__ == "__main__":
    raise SystemExit(
        run_main(
            __doc__ or "GA4GH demo",
            "artifacts/ga4gh.json",
            run,
        )
    )
