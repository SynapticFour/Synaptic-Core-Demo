"""CLI entry helper shared by demo scenarios."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable
from typing import Any

from lib.http import DemoError, write_report

DEMO_CONTAINER_IMAGE = os.environ.get("DEMO_CONTAINER_IMAGE", "busybox:1.36")


def run_main(
    description: str,
    default_out: str,
    run: Callable[..., dict[str, Any]],
    extra_args: Callable[[argparse.ArgumentParser], None] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--base-url", default=os.environ.get("SC_BASE_URL", "http://127.0.0.1:8080"))
    parser.add_argument("--out", default=default_out)
    if extra_args:
        extra_args(parser)
    args = parser.parse_args()
    kwargs = {k: v for k, v in vars(args).items() if k not in {"base_url", "out"}}
    try:
        report = run(args.base_url, **kwargs)
    except DemoError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    write_report(args.out, report)
    print(f"PASS {report.get('demo')} — complete")
    print(f"wrote {args.out}")
    return 0
