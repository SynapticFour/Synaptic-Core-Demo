# Evidence pack

Committed outputs are valid **only** when `META.json` has `"stale": false` and
the JSON states are `COMPLETE`. This pack was captured **2026-08-15** against
sibling Core that is now pin `1d48605` (TES GET reconcile / `get_task_fresh`).
See [`../EVIDENCE.md`](../EVIDENCE.md).

Refresh: `make demo-all && ./scripts/refresh-evidence.sh`.

| File | Contents |
|------|----------|
| `META.json` | UTC, Core SHA, dirty/patch note, `stale` flag |
| `health.json` | `/sc/health` |
| `ga4gh.json` / `stac.json` / `bids.json` | Fail-closed demo reports |
| `api_snapshots.json` | Follow-up GETs (same IDs, same session) |
| `console.txt` | `make demo-all` PASS lines |
| `ran_at_utc.txt` | Stamp |
