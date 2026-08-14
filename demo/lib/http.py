"""Shared HTTP helpers for Synaptic-Core-Demo scenarios."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


class DemoError(RuntimeError):
    pass


def request_json(
    method: str,
    url: str,
    body: dict[str, Any] | list[Any] | None = None,
    timeout: float = 30.0,
) -> tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            parsed: Any = json.loads(raw) if raw else None
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return e.code, parsed
    except urllib.error.URLError as e:
        raise DemoError(f"request failed: {method} {url}: {e}") from e


def require_ok(status: int, body: Any, what: str, ok: set[int] | None = None) -> Any:
    allowed = ok or {200, 201}
    if status not in allowed:
        raise DemoError(f"{what}: expected {sorted(allowed)}, got {status}: {body}")
    return body


def wait_health(base_url: str, timeout_s: float = 90.0) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    url = f"{base_url.rstrip('/')}/sc/health"
    last_err = "not started"
    while time.time() < deadline:
        try:
            status, body = request_json("GET", url, timeout=3.0)
            if status == 200 and isinstance(body, dict) and body.get("status") == "ok":
                return body
            last_err = f"status={status} body={body}"
        except DemoError as e:
            last_err = str(e)
        time.sleep(1.0)
    raise DemoError(f"health check timed out ({last_err})")


def write_report(path: str, report: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
