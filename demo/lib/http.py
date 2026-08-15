"""Shared HTTP helpers for Synaptic-Core-Demo scenarios.

Fail-closed: HTTP 2xx is not success. TES/WES success is terminal COMPLETE.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Iterable

CHOICE_A_ADAPTERS = ("ga4gh", "stac", "bids")
TERMINAL_OK = {"COMPLETE"}
TERMINAL_BAD = {
    "EXECUTOR_ERROR",
    "SYSTEM_ERROR",
    "CANCELED",
    "CANCELLED",
    "UNKNOWN",
}


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


def extract_id(value: Any, *keys: str) -> str:
    """Pull a string id out of Core JSON (string, wrapped newtype, or keyed object)."""
    if isinstance(value, str) and value.strip():
        return value
    if isinstance(value, dict):
        for key in keys or ("id", "run_id"):
            if key in value:
                return extract_id(value[key])
        inner = value.get("0")
        if isinstance(inner, str) and inner.strip():
            return inner
    raise DemoError(f"missing id in {value!r}")


def wait_health(
    base_url: str,
    timeout_s: float = 90.0,
    require_adapters: Iterable[str] = CHOICE_A_ADAPTERS,
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.time,
) -> dict[str, Any]:
    deadline = now_fn() + timeout_s
    url = f"{base_url.rstrip('/')}/sc/health"
    needed = list(require_adapters)
    last_err = "not started"
    while now_fn() < deadline:
        try:
            status, body = request_json("GET", url, timeout=3.0)
            if status == 200 and isinstance(body, dict) and body.get("status") == "ok":
                adapters = body.get("adapters") or []
                missing = [a for a in needed if a not in adapters]
                if missing:
                    last_err = f"missing adapters {missing}; have {adapters}"
                else:
                    return body
            else:
                last_err = f"status={status} body={body}"
        except DemoError as e:
            last_err = str(e)
        sleep_fn(1.0)
    raise DemoError(f"health check timed out ({last_err})")


def poll_until_complete(
    url: str,
    what: str,
    *,
    timeout_s: float = 120.0,
    interval_s: float = 0.5,
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.time,
) -> dict[str, Any]:
    """GET url until JSON.state is COMPLETE. RUNNING/QUEUED wait; anything else fails."""
    deadline = now_fn() + timeout_s
    last: Any = None
    while now_fn() < deadline:
        status, body = request_json("GET", url, timeout=10.0)
        body = require_ok(status, body, what)
        if not isinstance(body, dict):
            raise DemoError(f"{what}: expected object, got {body!r}")
        state = str(body.get("state") or "")
        last = body
        if state in TERMINAL_OK:
            return body
        if state in TERMINAL_BAD:
            raise DemoError(f"{what}: terminal failure state={state}: {body}")
        if state not in {"QUEUED", "INITIALIZING", "RUNNING", "PAUSED"}:
            raise DemoError(f"{what}: unexpected state={state!r}: {body}")
        sleep_fn(interval_s)
    raise DemoError(f"{what}: timed out waiting for COMPLETE (last={last})")


def require_complete(state: str | None, what: str) -> str:
    if state not in TERMINAL_OK:
        raise DemoError(f"{what}: expected COMPLETE, got {state!r}")
    return state


def write_report(path: str, report: dict[str, Any]) -> None:
    if not report.get("ok"):
        raise DemoError(f"refusing to write unsuccessful report to {path}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
