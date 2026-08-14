# Neuroimaging demo (BIDS)

## Who this is for

Imaging labs that publish **BIDS** datasets and run **BIDS Apps** (MRIQC, fMRIPrep, FreeSurfer wrappers).

## Story

1. Use the local minimal BIDS fixture (`fixtures/bids/minimal`) — the same layout `bids-validator` expects.
2. Read Synaptic Core’s HTTP index: `dataset_description`, `participants`, `derivatives`.
3. Submit a **BIDS-App-style** TES task that emits a QC summary JSON for the subjects.

Full fMRIPrep is deliberately not run: multi-GB images and long runtimes obscure the API story. The demo proves the contract labs need: **layout discovery + containerised app over that layout**.

## Run

```bash
make up-sibling
make demo-bids
cat artifacts/bids.json
```

Optional Stage C validator (Deno), same as Synaptic-Core-Test:

```bash
deno run -ERWN jsr:@bids/validator fixtures/bids/minimal
```

## Map to your work

| Your step | Demo analogue |
|-----------|---------------|
| `bids-validator` on disk | Fixture + optional Deno validator |
| Browse dataset metadata | `/bids/dataset_description`, `/bids/participants` |
| `docker run … mriqc bids_dir out participant` | TES task with BIDS tags |

## Limits

See [COVERAGE.md](../COVERAGE.md). Swap the busybox QC stub for a real BIDS App image when you are ready to burn CPU/GPU.
