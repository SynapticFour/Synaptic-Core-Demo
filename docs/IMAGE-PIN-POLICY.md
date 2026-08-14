# Image / Core pin policy

**Repo:** Synaptic-Core-Demo

## Policy

| Context | Rule |
|---------|------|
| **Synaptic-Core binary** | Pin SHA in `PINNED_VERSIONS.txt` (`Synaptic-Core-ref`). Sibling `../Synaptic-Core` for live-dev (`make up-sibling`). |
| **Choice A features** | Always build with `adapter-ga4gh,adapter-stac,adapter-bids`. |
| **Third-party images** | Pin postgres / minio / rust builder; no `:latest` on proof paths. |
| **Floating tags** | Forbidden for images that back demo claims. |

## Current pins

See [`PINNED_VERSIONS.txt`](../PINNED_VERSIONS.txt).

## Review

Monthly: [MONTHLY-DEPENDENCY-HYGIENE](https://github.com/SynapticFour/synapticfour-infra/blob/main/docs/MONTHLY-DEPENDENCY-HYGIENE.md).

**No Dependabot** in this repo — dependency updates are deliberate / reviewed (org policy).
