# Changelog

## [Unreleased]

### Changed
- Demos are fail-closed: TES/WES must reach `COMPLETE` or the process exits non-zero.
- README / walkthroughs describe laptop API smokes (echo stand-in), not samtools/NDVI/MRIQC.
- Default `make up` requires sibling `../Synaptic-Core`. Pinned clone is `make up-pinned`.
- Compose publishes only `127.0.0.1:8080`; Postgres unpublished; MinIO removed (unused).
- Docker CLI install is checksummed and arch-aware (amd64/arm64).
- `PINNED_VERSIONS.txt` is parsed by Makefile and CI; pin drift fails `ci-check`.
- BIDS demo ingests the fixture and requires live `/bids/participants` ObjectsService backing.
- STAC demo ingests a live Feature and requires `synaptic:backing=ObjectsService`.
- GA4GH WES `workflow_url` is the TRS descriptor of the registered echo tool.
- Evidence pack recorded 2026-08-15: all three demos `COMPLETE` (see `docs/EVIDENCE.md`). Requires sibling Core TES GET reconcile; pin `ffbc955` alone is not enough.
- `smoke-demos` runs on same-repo PRs and asserts report COMPLETE via `assert-reports.py`.
- PR CI runs unit tests, not only `compileall`.

### Added
- `tests/` for HTTP helpers and report contract.
- `NOTICE` (Apache-2.0 glue; BUSL-1.1 Core runtime).
- `scripts/refresh-evidence.sh`, `scripts/assert-reports.py`, `scripts/install-docker-cli.sh`.

### Security
- Loopback bind for the demo API. Docker socket remains required for TES/WES and is documented as local-only.
