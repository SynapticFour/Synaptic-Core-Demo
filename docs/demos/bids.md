# Neuroimaging demo (BIDS APIs)

Laptop smoke of BIDS HTTP index after **ingest**. Compute is **busybox echo**, not MRIQC.

The on-disk fixture (`fixtures/bids/minimal`) is the source of `sub-01` / age / sex. Core `/bids/dataset_description` is a **different** DemoStore document (`demo: true`). The live proof is `/bids/participants` after ingest (`backing: ObjectsService`).

The NIfTI is a 1×1×1 stub (layout + ingest bytes), not a brain volume.

## Story

1. Read `participants.tsv` from the fixture.
2. Assert HTTP `dataset_description` is the Core fixture (not the disk Name).
3. Ingest the stub NIfTI with BIDS metadata (`subject`, `modality`, `task`, `age`, `sex`).
4. GET `/bids/participants` — must be live ObjectsService with the same subject/age/sex.
5. TES echo until **COMPLETE**.

Optional disk validator (does not test Core):

```bash
deno run -ERWN jsr:@bids/validator fixtures/bids/minimal
```

## Run

```bash
make up-sibling
make demo-bids
cat artifacts/bids.json
```

## Limits

[`COVERAGE.md`](../COVERAGE.md).
