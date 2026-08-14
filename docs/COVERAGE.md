# Synaptic-Core-Demo coverage map

**Honesty:** This repo runs **real HTTP workflows** against Synaptic Core Choice A adapters. It is not the full conformance suite ([Synaptic-Core-Test](https://github.com/SynapticFour/Synaptic-Core-Test)) and not a production deployment guide.

**Pins:** [`PINNED_VERSIONS.txt`](../PINNED_VERSIONS.txt) · [`IMAGE-PIN-POLICY.md`](IMAGE-PIN-POLICY.md)

## What each demo proves

| Demo | Domain story | APIs exercised | Command |
|------|--------------|----------------|---------|
| `ga4gh_drs_wes` | Ingest → DRS → TRS → WES + TES | `/sc/objects`, `/ga4gh/drs`, `/ga4gh/trs`, `/ga4gh/wes`, `/ga4gh/tes`, `/sc/registry` | `make demo-ga4gh` |
| `stac_eo_search` | Catalogue search → item → process task | `/stac`, `/stac/search`, `/stac/collections/.../items`, `/ga4gh/tes` | `make demo-stac` |
| `bids_app_qc` | BIDS index → BIDS-App-style QC task | `/bids/*`, `/ga4gh/tes` + local fixture | `make demo-bids` |

Artifacts land in `artifacts/*.json` (gitignored).

## Forbidden claims

- Full production genomics pipelines (GATK Best Practices, GIAB truthsets)
- Full EO science (stackstac NDVI time series, Planetary Computer auth)
- Full fMRIPrep / FreeSurfer / MRIQC container runs (multi-GB images, hours of CPU)
- Regulatory certification, clinical clearance, or “GA4GH certified”
- That DemoStore seeds equal production object stores

## Internal use (bug finding)

If a demo fails against current `../Synaptic-Core`, prefer filing/fixing **Synaptic-Core** before softening the demo. Soften only when the gap is an explicit deferred claim in Core docs.

## CI expectation

| Workflow | When | What |
|----------|------|------|
| `ci` | every PR / push | `bash -n`, `compileall`, file presence |
| `smoke-demos` | `main` + `workflow_dispatch` | `make up-sibling` (or pin) + `make demo-all` when budget allows |

Default PR CI stays frugal (no cold Rust Core build).
