# Evidence — demos actually ran

This page is **not a claim sheet**. It records a concrete run of all three Choice A demos against a live Synaptic Core with `adapter-ga4gh`, `adapter-stac`, and `adapter-bids`.

| Field | Value |
|-------|--------|
| **UTC** | `2026-08-14T08:57:15Z` |
| **Core pin** | [`5f375d9`](https://github.com/SynapticFour/Synaptic-Core/commit/5f375d96367c8fe422cc975c13ea7e3ede8fb34e) |
| **Result** | All three demos: **`ok: true`** |
| **Raw pack** | [`docs/evidence/`](evidence/) |

Reproduce anytime:

```bash
make up-sibling    # or point SC_BASE_URL at any Choice A Core
make demo-all
# fresh outputs land in artifacts/ (gitignored)
```

---

## Console (verbatim)

```text
=== demo-ga4gh ===
PASS ga4gh — WES 01KZZQTS24GB1JPJT625PMJ77V TES 01KZZQTS25EGZZRRKPPJGWHMK1
wrote artifacts/evidence/ga4gh.json

=== demo-stac ===
PASS stac — item demo-item-1 task 01KZZQTTXRFJSV78HTHBHX70JK
wrote artifacts/evidence/stac.json

=== demo-bids ===
PASS bids — subjects ['sub-01'] task 01KZZQTV2NESTFWK3K0PXBRQ2R
wrote artifacts/evidence/bids.json
```

Source: [`evidence/console.log`](evidence/console.log)

---

## Health — Choice A adapters present

```json
{
  "status": "ok",
  "adapters": ["ga4gh", "stac", "bids"],
  "crates": {
    "sc-objects": "ok",
    "sc-tasks": "ok",
    "sc-workflows": "ok",
    "sc-registry": "ok",
    "sc-query": "ok",
    "sc-provenance": "ok"
  }
}
```

Full file: [`evidence/health.json`](evidence/health.json)

---

## 1) Genomics (GA4GH) — DRS → TRS → WES + TES

**Story:** ingest a tiny reads file → resolve via DRS → register a tool → fetch TRS descriptor → submit WES run → submit TES task.

| Step | Evidence ID |
|------|-------------|
| Object / DRS | `01KZZQTS21E7NZPJHX7SB5VA4E` |
| TRS tool | `01KZZQTS231VBTK7DNG6V8YAEK` (`demo-samtools-echo-…`) |
| WES run | `01KZZQTS24GB1JPJT625PMJ77V` → snapshot state **`COMPLETE`** |
| TES task | `01KZZQTS25EGZZRRKPPJGWHMK1` |

DRS object (live GET after demo):

```json
{
  "id": "01KZZQTS21E7NZPJHX7SB5VA4E",
  "name": "demo-reads.fastq.txt",
  "size": 23,
  "self_uri": "drs://synaptic-core/01KZZQTS21E7NZPJHX7SB5VA4E",
  "access_methods": [
    {
      "type": "stream",
      "access_url": {
        "url": "/sc/objects/v1/objects/01KZZQTS21E7NZPJHX7SB5VA4E/stream"
      }
    }
  ]
}
```

WES status snapshot:

```json
{
  "run_id": "01KZZQTS24GB1JPJT625PMJ77V",
  "state": "COMPLETE"
}
```

Reports: [`evidence/ga4gh.json`](evidence/ga4gh.json) · API snaps: [`evidence/api_snapshots.json`](evidence/api_snapshots.json)

Walkthrough for domain readers: [`demos/ga4gh.md`](demos/ga4gh.md)

---

## 2) Earth observation (STAC) — search → Item → process

**Story:** STAC landing/search over `demo-eo` (Berlin-ish bbox) → fetch Item → enqueue EO summary TES task.

| Step | Evidence |
|------|----------|
| Collection | `demo-eo` |
| Item | `demo-item-1` @ `2026-01-10T12:00:00Z` |
| Assets | `thumbnail` |
| Process task | `01KZZQTTXRFJSV78HTHBHX70JK` |

Item geometry (live GET):

```json
{
  "type": "Feature",
  "id": "demo-item-1",
  "collection": "demo-eo",
  "geometry": { "type": "Point", "coordinates": [13.405, 52.52] },
  "properties": {
    "datetime": "2026-01-10T12:00:00Z",
    "title": "Berlin demo item"
  }
}
```

Reports: [`evidence/stac.json`](evidence/stac.json) · Walkthrough: [`demos/stac.md`](demos/stac.md)

---

## 3) Neuroimaging (BIDS) — index → BIDS-App-style QC

**Story:** read `/bids/*` HTTP index for a minimal fixture → run a QC-summary TES task (MRIQC *contract*, not full fMRIPrep).

| Step | Evidence |
|------|----------|
| Fixture | `fixtures/bids/minimal` (`sub-01`) |
| HTTP `BIDSVersion` | `1.10.0` |
| HTTP `Name` | `Synaptic Core BIDS Adapter` |
| Participants | 1 (`sub-01`) |
| QC task | `01KZZQTV2NESTFWK3K0PXBRQ2R` |

Participants envelope (live GET):

```json
{
  "schema": ["participant_id", "age", "sex"],
  "participants": [
    {
      "participant_id": "sub-01",
      "age": 25,
      "sex": "F",
      "object_id": "sc-obj-bids-sub-01"
    }
  ]
}
```

Reports: [`evidence/bids.json`](evidence/bids.json) · Walkthrough: [`demos/bids.md`](demos/bids.md)

---

## How to refresh this pack

```bash
# against a running Choice A Core
export SC_BASE_URL=http://127.0.0.1:8080
mkdir -p artifacts/evidence docs/evidence
python3 demo/scenarios/ga4gh_drs_wes.py --out docs/evidence/ga4gh.json
python3 demo/scenarios/stac_eo_search.py --out docs/evidence/stac.json
python3 demo/scenarios/bids_app_qc.py --out docs/evidence/bids.json
# then re-snapshot health + API GETs and update this page
```

CI may also upload fresh `artifacts/*.json` from the `smoke-demos` workflow when that job runs on `main`.

## Honesty

- IDs and timestamps are from **one** local evidence run; they are not eternal production IDs.
- TES tasks may still show `RUNNING` at snapshot time if Docker has not finished; WES reached `COMPLETE` in this run.
- Scope limits remain in [`COVERAGE.md`](COVERAGE.md) — this page proves the demos execute, not that every scientific pipeline is included.
