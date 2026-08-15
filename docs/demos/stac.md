# Earth observation demo (STAC APIs)

Laptop smoke of STAC search plus live ObjectsService projection. Compute is **busybox echo**, not NDVI.

## Story

1. Hit `/stac` and require Core + Item Search `conformsTo`.
2. Search seeded `demo-eo`. If `demo-item-1` is present, its thumbnail must stay `example.com` (Core fixture).
3. Ingest a STAC Feature into collection `sc-demo-live`.
4. Require catalog `synaptic:backing` = `ObjectsService` and a search hit whose asset href is under `/sc/objects`.
5. TES echo until **COMPLETE**.

## Run

```bash
make up-sibling
make demo-stac
cat artifacts/stac.json
```

## Limits

[`COVERAGE.md`](../COVERAGE.md).
