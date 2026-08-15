#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8080}"
echo "waiting for ${BASE_URL}/sc/health (status=ok + adapters ga4gh,stac,bids) ..."
python3 - "$BASE_URL" <<'PY'
import json, sys, time, urllib.error, urllib.request

base = sys.argv[1].rstrip("/")
url = base + "/sc/health"
needed = ("ga4gh", "stac", "bids")
last = "not started"
for i in range(1, 91):
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")
        body = json.loads(raw) if raw else {}
        if status == 200 and body.get("status") == "ok":
            adapters = body.get("adapters") or []
            missing = [a for a in needed if a not in adapters]
            if not missing:
                print(f"healthy after {i}s")
                print(raw[:400])
                raise SystemExit(0)
            last = f"missing adapters {missing}; have {adapters}"
        else:
            last = f"status={status} body={body}"
    except urllib.error.URLError as e:
        last = str(e)
    except (json.JSONDecodeError, OSError) as e:
        last = str(e)
    time.sleep(1)
print(f"ERROR: health check timed out ({last})", file=sys.stderr)
raise SystemExit(1)
PY
