# Genomics demo (GA4GH APIs)

Laptop smoke of DRS / TRS / WES / TES. Compute is **busybox echo**, not samtools.

## Story

1. Ingest a 23-byte stand-in object.
2. Resolve it with DRS (`access_methods` required).
3. Register an echo tool; fetch it via TRS including a CWL descriptor.
4. Submit WES with `workflow_url` = that TRS descriptor URL and `steps` using the same image. Core **does not execute the CWL file**; it runs `steps`. The demo waits until state is **COMPLETE**.
5. Submit TES echo; wait until **COMPLETE**; assert GET image matches the pin.

## Run

```bash
make up-sibling
make demo-ga4gh
cat artifacts/ga4gh.json   # wes_state and tes_state must be COMPLETE
```

## Limits

[`COVERAGE.md`](../COVERAGE.md). Heavy callers live in Ferrum / Ferrum-GA4GH-Demo.
