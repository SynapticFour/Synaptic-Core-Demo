"""assert-reports.py contract tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import importlib.util


def _load():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "assert_reports", root / "scripts" / "assert-reports.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class ReportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load()

    def test_running_is_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ga4gh.json"
            path.write_text(
                json.dumps({"ok": True, "wes_state": "RUNNING", "tes_state": "COMPLETE"}),
                encoding="utf-8",
            )
            errs = self.mod.check_report(path)
        self.assertTrue(any("wes_state" in e for e in errs))

    def test_complete_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ga4gh.json"
            path.write_text(
                json.dumps({"ok": True, "wes_state": "COMPLETE", "tes_state": "COMPLETE"}),
                encoding="utf-8",
            )
            self.assertEqual(self.mod.check_report(path), [])

    def test_bids_requires_objects_service(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bids.json"
            path.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "qc_state": "COMPLETE",
                        "http_participants_backing": "fixture",
                    }
                ),
                encoding="utf-8",
            )
            errs = self.mod.check_report(path)
        self.assertTrue(any("http_participants_backing" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
