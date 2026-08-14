# Synaptic-Core-Demo

**Real workflows on Synaptic Core** — for genomics (GA4GH), Earth observation (STAC), and neuroimaging (BIDS).

This repo shows domain users what Synaptic Core can *do*, not only what it *claims*. Each demo walks a story you would recognize from your field, against a live Choice A stack (`adapter-ga4gh` + `adapter-stac` + `adapter-bids`).

| Domain | Demo | Real-world pattern it mirrors |
|--------|------|-------------------------------|
| Genomics / compute | [`demo/scenarios/ga4gh_drs_wes.py`](demo/scenarios/ga4gh_drs_wes.py) | GA4GH Starter Kit style: **DRS** object → **TRS** tool → **WES** run (+ **TES** task) |
| Earth observation | [`demo/scenarios/stac_eo_search.py`](demo/scenarios/stac_eo_search.py) | STAC catalogue search → item assets → lightweight process task (NDVI-style EO path) |
| Neuroimaging | [`demo/scenarios/bids_app_qc.py`](demo/scenarios/bids_app_qc.py) | BIDS dataset index → **BIDS-App-style** QC summary task (MRIQC analogy, not full fMRIPrep) |

**Proof, not prose:** a recorded run of all three demos (console + JSON + live API snapshots) lives in **[docs/EVIDENCE.md](docs/EVIDENCE.md)** / [`docs/evidence/`](docs/evidence/).

Product: [Synaptic-Core](https://github.com/SynapticFour/Synaptic-Core) · Conformance: [Synaptic-Core-Test](https://github.com/SynapticFour/Synaptic-Core-Test) · Org: [synapticfour.com](https://synapticfour.com)

> **Legal notice:** This README describes technical capabilities for demonstration. It is not legal advice, regulatory certification, or a compliance guarantee. Outcomes depend on operator configuration and organisational controls.

## Quick start

**Prerequisites:** Docker, ~4 GB RAM, ports **8080**, **5432**, **9000** free. Sibling checkout of Synaptic-Core recommended for development.

```bash
git clone https://github.com/SynapticFour/Synaptic-Core-Demo.git
cd Synaptic-Core-Demo

# Prefer live sibling Core (Choice A features baked in)
make up-sibling

# Run all domain demos
make demo-all
```

API: http://localhost:8080 · Health: http://localhost:8080/sc/health

| Goal | Command |
|------|---------|
| Start from sibling `../Synaptic-Core` | `make up-sibling` |
| Start from pinned Core SHA | `make up` |
| Stop / wipe volumes | `make down` / `make reset` |
| One demo | `make demo-ga4gh` · `make demo-stac` · `make demo-bids` |
| Syntax-only CI parity | `make smoke-syntax` |

## What you will see

### Genomics (GA4GH)

Ingest a small data object, resolve it via **DRS**, register a tool in **TRS**, then submit a **WES** run (CWL-shaped steps) and a **TES** task — the same cloud API vocabulary as the [GA4GH Get-Started / Starter Kit](https://github.com/ga4gh/Get-Started-with-GA4GH-APIs) cookbooks (samtools-on-DRS → WES), adapted to Synaptic Core’s `/sc/*` fabric.

### Earth observation (STAC)

Discover the demo EO catalogue (`demo-eo`), search by bbox/datetime like Element84 / Planetary Computer tutorials, fetch an Item, then enqueue a lightweight “scene summary” task — catalogue discovery → compute, without downloading a full archive.

### Neuroimaging (BIDS)

Index a minimal BIDS dataset (layout + participants), then run a BIDS-App-shaped QC summary task — the same *contract* as MRIQC/fMRIPrep (containerised app over a BIDS root), scaled for a laptop demo.

## Honesty

See [`docs/COVERAGE.md`](docs/COVERAGE.md) for what these demos prove vs forbid. They are also an internal **bug-finding harness** for Synaptic-Core inefficiencies — if a demo fails, treat it as a Core issue until proven otherwise.

## Docs

| Doc | Purpose |
|-----|---------|
| **[docs/EVIDENCE.md](docs/EVIDENCE.md)** | **Recorded run** — console + IDs + API snapshots |
| [docs/demos/ga4gh.md](docs/demos/ga4gh.md) | Genomics walkthrough |
| [docs/demos/stac.md](docs/demos/stac.md) | EO walkthrough |
| [docs/demos/bids.md](docs/demos/bids.md) | Neuroimaging walkthrough |
| [docs/ECOSYSTEM.md](docs/ECOSYSTEM.md) | Synaptic Core stack map |
| [docs/COVERAGE.md](docs/COVERAGE.md) | What demos prove vs forbid |
| [docs/IMAGE-PIN-POLICY.md](docs/IMAGE-PIN-POLICY.md) | Image / Core SHA pins |
| [PINNED_VERSIONS.txt](PINNED_VERSIONS.txt) | Exact pins |

## License

Apache-2.0 — Synaptic Four · [contact@synapticfour.com](mailto:contact@synapticfour.com)
