# Image / Core pin policy

**Repo:** Synaptic-Core-Demo

## Policy

| Context | Rule |
|---------|------|
| **Synaptic-Core binary** | SHA in `PINNED_VERSIONS.txt` (`Synaptic-Core-ref`). Makefile exports it. `make up` uses sibling `../Synaptic-Core`. `make up-pinned` clones that SHA (private repo). Pin includes TES GET reconcile (`get_task_fresh`) required for `COMPLETE`. |
| **Choice A features** | Always `adapter-ga4gh,adapter-stac,adapter-bids`. |
| **Third-party images** | Pin postgres / rust builder / busybox / docker CLI (checksums in `PINNED_VERSIONS.txt`). |
| **Floating tags** | Forbidden for images that back demo claims (`:latest` never). |
| **Host publish** | API on `127.0.0.1:8080` only. Postgres unpublished. No MinIO. |

`scripts/hooks/ci-check.sh` fails if Dockerfile / compose SHA or docker CLI checksums drift from `PINNED_VERSIONS.txt`.

## Review

Monthly: [MONTHLY-DEPENDENCY-HYGIENE](https://github.com/SynapticFour/synapticfour-infra/blob/main/docs/MONTHLY-DEPENDENCY-HYGIENE.md).

**No Dependabot** in this repo — dependency updates are deliberate / reviewed (org policy).
