"""
GA4GH demo — genomics / scientific compute path.

Mirrors the GA4GH Starter Kit / Get-Started cookbooks:
  ingest data → DRS resolve → TRS register tool → WES run (+ TES task)

Real-world analogues: samtools-on-DRS → WES submission tutorials.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo"))

from lib.http import DemoError, request_json, require_ok, wait_health, write_report  # noqa: E402


def run(base_url: str) -> dict:
    base = base_url.rstrip("/")
    health = wait_health(base)
    adapters = health.get("adapters") or []
    if "ga4gh" not in adapters:
        raise DemoError(f"adapter-ga4gh not enabled; adapters={adapters}")

    # 1) Ingest a tiny "sequencing sidecar" object via /sc/objects
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
    obj = require_ok(status, body, "ingest")
    object_id = obj.get("id") if isinstance(obj.get("id"), str) else (obj.get("id") or {}).get("0")
    if not object_id:
        raise DemoError(f"ingest missing id: {obj}")

    # 2) Resolve via DRS (GA4GH data plane)
    status, drs = request_json("GET", f"{base}/ga4gh/drs/v1/objects/{object_id}")
    drs = require_ok(status, drs, "DRS get")
    if not (drs.get("access_methods") or []):
        raise DemoError("DRS object has no access_methods")

    # 3) Register a tool in Core registry → visible via TRS
    tool_name = f"demo-samtools-echo-{int(time.time())}"
    status, tool = request_json(
        "POST",
        f"{base}/sc/registry/v1/tools",
        {
            "name": tool_name,
            "version": "1.0.0",
            "container_image": "busybox:1.36",
            "description": "Demo stand-in for a samtools-style CLI tool",
            "metadata": {"domain": "genomics"},
        },
    )
    tool = require_ok(status, tool, "register tool")
    tool_id = tool.get("id")
    if not tool_id:
        raise DemoError(f"tool missing id: {tool}")

    status, trs_tool = request_json("GET", f"{base}/ga4gh/trs/v2/tools/{tool_id}")
    trs_tool = require_ok(status, trs_tool, "TRS get tool")

    status, desc = request_json(
        "GET",
        f"{base}/ga4gh/trs/v2/tools/{tool_id}/versions/1.0.0/CWL/descriptor",
    )
    desc = require_ok(status, desc, "TRS descriptor")

    # 4) WES run — CWL-shaped steps (Starter Kit style submission)
    wes_payload = {
        "workflow_url": "file://workflows/echo.cwl",
        "workflow_type": "cwl",
        "workflow_params": {"input_drs_id": object_id},
        "steps": [
            {
                "name": "count-bases-placeholder",
                "container_image": "busybox:1.36",
                "command": ["sh", "-c", "echo ga4gh-demo-ok"],
            }
        ],
    }
    status, run = request_json("POST", f"{base}/ga4gh/wes/v1/runs", wes_payload)
    run = require_ok(status, run, "WES create", ok={200, 201})
    run_id = run.get("run_id") or run.get("id")
    if not run_id:
        raise DemoError(f"WES missing run_id: {run}")

    status, run_status = request_json("GET", f"{base}/ga4gh/wes/v1/runs/{run_id}/status")
    run_status = require_ok(status, run_status, "WES status")

    # 5) TES task — single-container job (Cloud TES vocabulary)
    tes_payload = {
        "name": "demo-tes-echo",
        "executors": [{"image": "busybox:1.36", "command": ["echo", "tes-demo-ok"]}],
        "inputs": [{"url": f"drs://synaptic-core/{object_id}"}],
    }
    status, task = request_json("POST", f"{base}/ga4gh/tes/v1/tasks", tes_payload)
    task = require_ok(status, task, "TES create", ok={200, 201})
    task_id = task.get("id")
    if not task_id:
        raise DemoError(f"TES missing id: {task}")

    status, task_get = request_json("GET", f"{base}/ga4gh/tes/v1/tasks/{task_id}")
    task_get = require_ok(status, task_get, "TES get")

    return {
        "demo": "ga4gh_drs_wes",
        "story": "DRS object → TRS tool → WES run + TES task",
        "object_id": object_id,
        "drs_id": drs.get("id"),
        "tool_id": tool_id,
        "trs_tool_name": trs_tool.get("name"),
        "trs_descriptor_type": desc.get("type"),
        "wes_run_id": run_id,
        "wes_state": run_status.get("state"),
        "tes_task_id": task_id,
        "tes_state": task_get.get("state"),
        "ok": True,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default="http://127.0.0.1:8080")
    p.add_argument("--out", default="artifacts/ga4gh.json")
    args = p.parse_args()
    try:
        report = run(args.base_url)
    except DemoError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    write_report(args.out, report)
    print(f"PASS ga4gh — WES {report['wes_run_id']} TES {report['tes_task_id']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
