# Evidence — recorded COMPLETE run (2026-08-15)

This page is both the **contract** and the **last recorded proof**. IDs below
come from [`docs/evidence/`](evidence/) written in the same session as
`make demo-all`. They are not later GETs cherry-picked after a `RUNNING` report.

A run counts as evidence only if:

1. `make demo-all` exits 0.
2. `ga4gh.json` has `wes_state` and `tes_state` equal to `COMPLETE`.
3. `stac.json` has `process_state` equal to `COMPLETE`.
4. `bids.json` has `qc_state` equal to `COMPLETE` and
   `http_participants_backing` equal to `ObjectsService`.
5. `scripts/assert-reports.py` agrees.
6. `docs/evidence/META.json` has `"stale": false`.

HTTP 201 + `RUNNING` is a **failure**. Do not copy a later GET into the narrative.

## This pack

| Field | Value |
|-------|--------|
| UTC | `2026-08-15T09:54:48Z` |
| Host API | `http://127.0.0.1:8080` |
| Health | `status=ok`, adapters `ga4gh,stac,bids`, `sc_specs_version` **1.1.0** |
| Core tree | `ffbc955cb611bf9bb2ddf7dafe84ab96a0213a79` **plus uncommitted TES GET reconcile** |
| Compute | pinned `busybox:1.36` echo (not samtools / NDVI / MRIQC) |
| Assert | `scripts/assert-reports.py` pass on the three reports |

**Core requirement:** TES `GET /ga4gh/tes/v1/tasks/{id}` must call
`TaskService::get_task_fresh` (docker inspect + persist COMPLETE). WES already
waited on inspect; TES GET used to return the DB row only, so containers could
be `Exited (0)` while TES stayed `RUNNING` until process restart. That patch
is in the sibling working tree (`crates/synaptic-core-tasks`,
`crates/synaptic-core-gateway`) and is **not** in the published pin yet.
`make up-pinned` against `PINNED_VERSIONS.txt` (`ffbc955…`) will **not**
reproduce this pack.

Machine files: [`evidence/META.json`](evidence/META.json) ·
[`evidence/health.json`](evidence/health.json) ·
[`evidence/ga4gh.json`](evidence/ga4gh.json) ·
[`evidence/stac.json`](evidence/stac.json) ·
[`evidence/bids.json`](evidence/bids.json) ·
[`evidence/api_snapshots.json`](evidence/api_snapshots.json).

## GA4GH

Claim: ingest → DRS resolve → TRS register echo tool → WES + TES **COMPLETE**.
Not claimed: samtools / GATK / Dockstore.

| What | ID / value | State |
|------|------------|--------|
| DRS object | `01M02DEBT90KTJCPFSC9PY7CSS` (`demo-reads.fastq.txt`, 23 bytes) | GET 200, stream access_method |
| TRS tool | `01M02DECJRN7XFDR6C4A06Z7PH` (`sc-demo-echo-1786787607`) | GET 200 |
| WES run | `01M02DECPC2TNJ9ZESKRCMJKJD` | **COMPLETE** (status + run GET) |
| WES `workflow_url` | TRS CWL descriptor of that tool | stored; Core runs `steps`, not the CWL file |
| TES task | `01M02DEQMV6KCSQ6SE56ZGYQ86` | **COMPLETE**, image `busybox:1.36`, `echo tes-demo-ok` |

Same IDs in the report JSON and in the follow-up GETs in `api_snapshots.json`.

## STAC

Claim: fixture `demo-eo` / `example.com` distinguished from a live Feature
projected from ObjectsService; TES **COMPLETE**. Not claimed: NDVI / stackstac.

| What | Value |
|------|--------|
| During demo, fixture item | `demo-item-1`, thumbnail `https://example.com/demo-item-1.jpg` |
| After ingest, catalog | `/stac` `synaptic:backing` = **ObjectsService** |
| Live item | `sc-demo-live` / `sc-demo-live-1` |
| Live object | `01M02DF0RSGR697CPY6994KY1G` (asset href under `/sc/objects/…/stream`) |
| Process TES | `01M02DF0Z1CTZ0A37M01F40DGW` **COMPLETE** |

Post-run honesty: `GET /stac/collections/demo-eo/items/demo-item-1` is **404**
once the catalog is live ObjectsService. The fixture thumbnail is recorded in
`stac.json` from the search **before** ingest, not from a later item GET.

## BIDS

Claim: fixture TSV ingested; `/bids/participants` is ObjectsService with the
same subject/age/sex; TES **COMPLETE**. Not claimed: MRIQC / fMRIPrep.

| What | Value |
|------|--------|
| On-disk fixture | `fixtures/bids/minimal` (`Name`: Synaptic Core BIDS Fixture, `sub-01`) |
| HTTP `dataset_description` | still Core DemoStore (`Name`: Synaptic Core BIDS Adapter, `demo=true`) |
| HTTP `participants` | `backing=ObjectsService`, `demo=false` |
| Live row | `participant_id=sub-01`, `age=30`, `sex=M`, `object_id=01M02DFBPQJR46YW5PN7V21ECB` |
| QC TES | `01M02DFC2005D0JYCCPQZPSZTQ` **COMPLETE** |

## Refresh

```bash
make up-sibling    # requires ../Synaptic-Core including TES GET reconcile
make demo-all
./scripts/refresh-evidence.sh
```

`make evidence` re-runs `demo-all` then the same copy. Do not point
`synaptic_core_ref` at a SHA that cannot reach COMPLETE.

CI uploads `artifacts/*.json` from `smoke-demos`. Those files are the live
proof for a SHA. Committed `docs/evidence/*` is only valid when `stale` is
false and the JSON states match this page.

Walkthroughs: [`demos/ga4gh.md`](demos/ga4gh.md) ·
[`demos/stac.md`](demos/stac.md) · [`demos/bids.md`](demos/bids.md).
