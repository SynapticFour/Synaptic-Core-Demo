# Changelog

## [Unreleased]

### Changed
- Bump Synaptic-Core pin to `ffbc955` (live catalogues / specs 1.1.0 follow-ups).
- Require `SF_REPO_READ_TOKEN` for private Core checkout in `smoke-demos`.
- Mount host Docker socket + ship `docker` CLI in the Core runtime image so TES demos work in CI.

### Added
- Initial Synaptic-Core-Demo: Choice A stack (GA4GH + STAC + BIDS) with real workflow demos.
- `demo-ga4gh` — DRS → TRS → WES/TES (Starter Kit–style genomics path).
- `demo-stac` — STAC search → Item → process task (EO catalogue path).
- `demo-bids` — BIDS HTTP index → BIDS-App-style QC task.
- Pre-commit CI parity, frugal `ci` workflow, optional `smoke-demos` on main.
- Docs: COVERAGE, ECOSYSTEM, IMAGE-PIN-POLICY, per-domain walkthroughs.
- Committed evidence pack (`docs/EVIDENCE.md`, `docs/evidence/*`) from a live all-green demo run.
