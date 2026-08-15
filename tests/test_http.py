"""Unit tests for fail-closed HTTP helpers. No live Core required."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from demo.lib.http import (
    DemoError,
    extract_id,
    poll_until_complete,
    require_complete,
    require_ok,
    wait_health,
    write_report,
)


class ExtractIdTests(unittest.TestCase):
    def test_string(self) -> None:
        self.assertEqual(extract_id("abc"), "abc")

    def test_keyed(self) -> None:
        self.assertEqual(extract_id({"run_id": "r1"}, "run_id", "id"), "r1")

    def test_newtype_zero(self) -> None:
        self.assertEqual(extract_id({"0": "ulid-1"}), "ulid-1")

    def test_missing(self) -> None:
        with self.assertRaises(DemoError):
            extract_id({})


class RequireOkTests(unittest.TestCase):
    def test_accepts_201(self) -> None:
        self.assertEqual(require_ok(201, {"id": "x"}, "create"), {"id": "x"})

    def test_rejects_500(self) -> None:
        with self.assertRaises(DemoError):
            require_ok(500, {"error": "nope"}, "TES create")


class CompleteTests(unittest.TestCase):
    def test_complete_ok(self) -> None:
        self.assertEqual(require_complete("COMPLETE", "WES"), "COMPLETE")

    def test_running_fails(self) -> None:
        with self.assertRaises(DemoError):
            require_complete("RUNNING", "WES")

    def test_write_report_rejects_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "out.json")
            with self.assertRaises(DemoError):
                write_report(path, {"ok": False, "wes_state": "RUNNING"})
            self.assertFalse(Path(path).exists())

    def test_write_report_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "out.json")
            write_report(path, {"ok": True, "wes_state": "COMPLETE"})
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertTrue(data["ok"])


class PollTests(unittest.TestCase):
    def test_poll_reaches_complete(self) -> None:
        states = iter(
            [
                (200, {"state": "QUEUED"}),
                (200, {"state": "RUNNING"}),
                (200, {"state": "COMPLETE"}),
            ]
        )

        def fake_request(method: str, url: str, timeout: float = 30.0):
            return next(states)

        with patch("demo.lib.http.request_json", fake_request):
            body = poll_until_complete(
                "http://x/status",
                "WES",
                sleep_fn=lambda _s: None,
                now_fn=lambda: 0.0,
                timeout_s=10,
            )
        self.assertEqual(body["state"], "COMPLETE")

    def test_poll_executor_error_fails(self) -> None:
        def fake_request(method: str, url: str, timeout: float = 30.0):
            return 200, {"state": "EXECUTOR_ERROR", "id": "t"}

        with patch("demo.lib.http.request_json", fake_request):
            with self.assertRaises(DemoError) as ctx:
                poll_until_complete(
                    "http://x/task",
                    "TES",
                    sleep_fn=lambda _s: None,
                    now_fn=lambda: 0.0,
                )
        self.assertIn("EXECUTOR_ERROR", str(ctx.exception))

    def test_poll_timeout_on_running(self) -> None:
        clock = {"t": 0.0}

        def now() -> float:
            return clock["t"]

        def sleep(_s: float) -> None:
            clock["t"] += 50.0

        def fake_request(method: str, url: str, timeout: float = 30.0):
            return 200, {"state": "RUNNING"}

        with patch("demo.lib.http.request_json", fake_request):
            with self.assertRaises(DemoError) as ctx:
                poll_until_complete(
                    "http://x/status",
                    "WES",
                    timeout_s=10,
                    sleep_fn=sleep,
                    now_fn=now,
                )
        self.assertIn("timed out", str(ctx.exception))


class HealthTests(unittest.TestCase):
    def test_requires_choice_a_adapters(self) -> None:
        def fake_request(method: str, url: str, timeout: float = 30.0):
            return 200, {"status": "ok", "adapters": ["ga4gh"]}

        clock = {"t": 0.0}

        def now() -> float:
            return clock["t"]

        def sleep(_s: float) -> None:
            clock["t"] += 100.0

        with patch("demo.lib.http.request_json", fake_request):
            with self.assertRaises(DemoError) as ctx:
                wait_health(
                    "http://127.0.0.1:8080",
                    timeout_s=1,
                    sleep_fn=sleep,
                    now_fn=now,
                )
        self.assertIn("missing adapters", str(ctx.exception))

    def test_ok_when_all_present(self) -> None:
        body = {"status": "ok", "adapters": ["ga4gh", "stac", "bids"]}

        def fake_request(method: str, url: str, timeout: float = 30.0):
            return 200, body

        with patch("demo.lib.http.request_json", fake_request):
            got = wait_health(
                "http://127.0.0.1:8080",
                timeout_s=5,
                sleep_fn=lambda _s: None,
            )
        self.assertEqual(got, body)


if __name__ == "__main__":
    unittest.main()
