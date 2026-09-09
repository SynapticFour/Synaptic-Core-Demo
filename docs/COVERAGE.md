# Synaptic-Core-Demo coverage map

**Honesty:** This repo runs **fail-closed HTTP smokes** against Synaptic Core Choice A adapters. Success means TES/WES **COMPLETE**, not HTTP 201. It is not the conformance suite ([Synaptic-Core-Test](https://github.com/SynapticFour/Synaptic-Core-Test)) and not a production deployment guide.

**Pins:** [`PINNED_VERSIONS.txt`](../PINNED_VERSIONS.txt) is the source of truth (Makefile + CI parse it).

## What each demo proves

| Demo | Asserts | Does not assert |
|------|---------|-----------------|
| `ga4gh_drs_wes` | Ingest, DRS `access_methods`, TRS get, WES `workflow_url` = TRS descriptor, WES **COMPLETE**, TES **COMPLETE**, TES image = pinned busybox | samtools, GATK, Dockstore, CWL file execution |
| `stac_eo_search` | STAC core+search conformance; fixture `demo-eo` thumbnail is `example.com` when present; ingest live Feature; catalog `synaptic:backing=ObjectsService`; live item asset href under `/sc/objects`; TES **COMPLETE** | NDVI, stackstac, Planetary Computer, real COGs |
| `bids_app_qc` | On-disk fixture TSV ingested with `subject`/`modality`/`task`; `/bids/participants` `backing=ObjectsService` and same age/sex; `/bids/dataset_description` remains Core fixture (`demo=true`); TES **COMPLETE** | MRIQC, fMRIPrep, bids-validator-as-Core, layout HTTP = disk Name |

Artifacts: `artifacts/*.json` (gitignored). The committed pack is [`docs/EVIDENCE.md`](EVIDENCE.md) / [`docs/evidence/`](evidence/). Refresh with `make evidence` after a green `demo-all`.

## Forbidden claims

- Full production genomics pipelines (GATK Best Practices, GIAB truthsets)
- Full EO science (stackstac NDVI time series, Planetary Computer auth)
- Full fMRIPrep / FreeSurfer / MRIQC container runs
- Regulatory certification or clinical clearance
- That DemoStore seeds equal production object stores
- That Core WES executes `workflows/echo.cwl` (WES requires `steps`; `workflow_url` is stored, not fetched)
- That TES GET `name` is the client-supplied task name (Core maps `name` to container image)
- That `/bids/dataset_description` is the on-disk fixture (it is a Core DemoStore document)

## Known Core shapes the demos encode

- WES create requires non-empty `steps`.
- TES GET must reconcile docker inspect (`get_task_fresh`) or state stays `RUNNING` after `Exited (0)`. Pin `1d48605` includes that.
- TES GET returns `executors[0].image` / `command` / `state`; inputs are accepted on create and not echoed on GET.
- BIDS `dataset_description` is always the adapter fixture; live catalogue is `participants` / `derivatives` after BIDS-shaped ingest.
- STAC fixture item uses `https://example.com/demo-item-1.jpg` until live objects exist.

## Internal use (bug finding)

If a demo fails against current `../Synaptic-Core`, prefer filing/fixing **Synaptic-Core** before softening the demo. Soften only when the gap is an explicit deferred claim in Core docs.

## CI expectation

| Workflow | When | What |
|----------|------|------|
| `ci` | every PR / push | `compileall`, **unittest**, pin consistency, `compose config` |
| `smoke-demos` | `main`, same-repo PRs, `workflow_dispatch` | sibling Core build + `demo-all` + `assert-reports.py` (COMPLETE) |

`smoke-demos` clones public Synaptic-Core at the pin. Fork PRs skip that job.
