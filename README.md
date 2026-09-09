# Synaptic-Core-Demo

Laptop checks for **Synaptic Core** adapters: GA4GH, STAC, BIDS.

Each demo talks to real Core HTTP APIs and **passes only when TES/WES reach `COMPLETE`**. Compute is a pinned `busybox` echo so a laptop can prove the lifecycle.

| Domain | Demo | What it actually asserts |
|--------|------|--------------------------|
| Genomics APIs | [`demo/scenarios/ga4gh_drs_wes.py`](demo/scenarios/ga4gh_drs_wes.py) | Ingest → **DRS** → **TRS** register → **WES** + **TES** until **COMPLETE** (echo stand-in) |
| Earth observation APIs | [`demo/scenarios/stac_eo_search.py`](demo/scenarios/stac_eo_search.py) | Fixture `demo-eo` vs **live** STAC projection after ingest; TES **COMPLETE** |
| Neuroimaging APIs | [`demo/scenarios/bids_app_qc.py`](demo/scenarios/bids_app_qc.py) | Fixture TSV ingested; `/bids/participants` is **ObjectsService** with the same subject/age/sex; TES **COMPLETE** |

Product: [Synaptic-Core](https://github.com/SynapticFour/Synaptic-Core) (public, BUSL-1.1) · Conformance: [Synaptic-Core-Test](https://github.com/SynapticFour/Synaptic-Core-Test) · Org: [synapticfour.com](https://synapticfour.com)

> **Legal notice:** Demonstration of technical APIs. Not legal advice, certification, or a compliance guarantee. See [NOTICE](NOTICE).

## Quick start

**Prerequisites:** Docker, ~4 GB RAM, a sibling checkout of **Synaptic-Core**.
API binds **127.0.0.1:8080** only. TES/WES mount the host Docker socket (local demo only).

```bash
# Core must sit next to this repo (public clone)
git clone https://github.com/SynapticFour/Synaptic-Core.git
git clone https://github.com/SynapticFour/Synaptic-Core-Demo.git
cd Synaptic-Core-Demo

make up          # == up-sibling when ../Synaptic-Core exists
make demo-all    # fails if any job is still RUNNING
```

API: http://127.0.0.1:8080 · Health: http://127.0.0.1:8080/sc/health

| Goal | Command |
|------|---------|
| Sibling `../Synaptic-Core` | `make up` / `make up-sibling` |
| Pinned Core SHA (public clone of Synaptic-Core) | `make up-pinned` |
| Stop / wipe volumes | `make down` / `make reset` |
| One demo | `make demo-ga4gh` · `make demo-stac` · `make demo-bids` |
| Unit tests + pin check | `make smoke-syntax` |

`make up-pinned` git-clones `SynapticFour/Synaptic-Core` at the SHA in `PINNED_VERSIONS.txt`. A laptop clone does not need an org token. GitHub Actions uses the default `GITHUB_TOKEN` for that public checkout.

## Honesty

See [`docs/COVERAGE.md`](docs/COVERAGE.md). Core WES **requires `steps`** and does not execute a CWL file from `workflow_url`. TES GET maps `name` to the container image. `/bids/dataset_description` stays a Core fixture; live proof is `/bids/participants` after ingest. Seeded STAC `demo-item-1` uses `example.com` — the demo also ingests a live item so ObjectsService backing can be asserted.

If a demo fails against current `../Synaptic-Core`, treat it as a **Core issue** until proven otherwise.

## Docs

| Doc | Purpose |
|-----|---------|
| [docs/EVIDENCE.md](docs/EVIDENCE.md) | Recorded COMPLETE run (2026-08-15) + refresh contract |
| [docs/demos/ga4gh.md](docs/demos/ga4gh.md) | GA4GH walkthrough |
| [docs/demos/stac.md](docs/demos/stac.md) | STAC walkthrough |
| [docs/demos/bids.md](docs/demos/bids.md) | BIDS walkthrough |
| [docs/ECOSYSTEM.md](docs/ECOSYSTEM.md) | Stack map |
| [docs/COVERAGE.md](docs/COVERAGE.md) | Prove vs forbid |
| [docs/IMAGE-PIN-POLICY.md](docs/IMAGE-PIN-POLICY.md) | Pins |
| [PINNED_VERSIONS.txt](PINNED_VERSIONS.txt) | Exact pins (Makefile/CI source) |

## License

Apache-2.0 for this repo — Synaptic Four · [contact@synapticfour.com](mailto:contact@synapticfour.com). Runtime Core is BUSL-1.1; see [NOTICE](NOTICE).
