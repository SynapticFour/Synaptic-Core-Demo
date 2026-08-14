# Genomics demo (GA4GH)

## Who this is for

Bioinformaticians and platform engineers who already know **DRS / WES / TES / TRS** (or the [GA4GH Starter Kit](https://starterkit.ga4gh.org/) cookbooks).

## Story

1. Ingest a small data object into Synaptic Core (`/sc/objects`).
2. Resolve it with **DRS** (`/ga4gh/drs/v1/objects/{id}`).
3. Register a CLI tool and fetch it via **TRS** (including a CWL descriptor).
4. Submit a **WES** run with CWL-shaped steps (same vocabulary as Nextflow/CWL WES tutorials).
5. Submit a **TES** task for a single-container job.

This is the portable-cloud path labs use when moving from “ssh + docker” to standards-based APIs — without claiming a full GATK Best Practices pipeline.

## Run

```bash
make up-sibling   # Choice A Core
make demo-ga4gh
cat artifacts/ga4gh.json
```

## Map to your work

| Your step | Demo analogue |
|-----------|---------------|
| Stage BAM/CRAM in object store | `/sc/objects` ingest → DRS id |
| Discover tools on Dockstore | TRS list/get + descriptor |
| Launch CWL/WDL/Nextflow remotely | WES `POST /runs` |
| Run one container job | TES `POST /tasks` |

## Limits

See [COVERAGE.md](../COVERAGE.md). Heavy callers (GATK, GIAB) live in Ferrum / Ferrum-GA4GH-Demo territory.
