# Earth observation demo (STAC)

## Who this is for

Remote-sensing scientists and EO platform engineers who use **STAC API** catalogues (Element84 Earth Search, Microsoft Planetary Computer, Copernicus CDSE).

## Story

1. Hit the STAC landing page and check `conformsTo` (Core + Item Search).
2. List collections and confirm the seeded `demo-eo` collection.
3. **Search** by bbox + datetime (Berlin-ish window) — same pattern as Sentinel-2 tutorials.
4. Fetch the Item and inspect assets.
5. Enqueue a lightweight **process task** (TES) that would, in production, stand in for NDVI / cloud mask / Application Package execution.

## Run

```bash
make up-sibling
make demo-stac
cat artifacts/stac.json
```

## Map to your work

| Your step | Demo analogue |
|-----------|---------------|
| `pystac_client` search | `POST /stac/search` |
| Open Item COG assets | Item `assets` map |
| OGC Processes / CWL EO Apps | TES process task (stand-in) |

## Limits

No full `stackstac` / `xarray` cube or Planetary Computer SAS tokens — see [COVERAGE.md](../COVERAGE.md).
