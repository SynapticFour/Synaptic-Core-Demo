# Contributing

## How to contribute

- Open an issue before large changes.
- Use focused branches and small PRs. Do not push proof/evidence edits straight to `main` if a second reader is available.
- Demo success is **COMPLETE**, not HTTP 2xx. Do not weaken `poll_until_complete`.
- If a demo fails against `../Synaptic-Core`, treat it as a Core bug until proven otherwise.

## Local gates (must pass before PR)

```bash
make smoke-syntax    # compileall + unittest + pin consistency
```

Stack changes:

```bash
make up-sibling
make demo-all        # fail-closed; writes artifacts/*.json
```

CI on every PR runs `make smoke-syntax`. Same-repo PRs also run `smoke-demos` (clones public Synaptic-Core at the pin).

## Pull request checklist

- Problem statement
- Unit tests for helper changes; live demo for scenario/API changes
- Docs updated (`COVERAGE.md` if claims change)
- No unrelated refactors

## License

Contributions are licensed under this repository's Apache-2.0 license.
The Core binary you run is BUSL-1.1; see NOTICE.
