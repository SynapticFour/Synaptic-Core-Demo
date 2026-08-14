#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPYCACHEPREFIX="${ROOT}/.cache/pyc"
mkdir -p "$PYTHONPYCACHEPREFIX"
echo "ci-check: compileall"
python3 -m compileall -q demo/lib demo/scenarios
echo "ci-check: bash -n"
bash -n scripts/wait-healthy.sh
bash -n scripts/hooks/ci-check.sh
echo "ci-check: required files"
test -f README.md
test -f PINNED_VERSIONS.txt
test -f docs/COVERAGE.md
test -f docs/IMAGE-PIN-POLICY.md
test -f demo/scenarios/ga4gh_drs_wes.py
test -f demo/scenarios/stac_eo_search.py
test -f demo/scenarios/bids_app_qc.py
test -f fixtures/bids/minimal/dataset_description.json
echo "ci-check: OK"
