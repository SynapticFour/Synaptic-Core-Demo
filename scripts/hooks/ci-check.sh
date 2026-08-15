#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPYCACHEPREFIX="${ROOT}/.cache/pyc"
mkdir -p "$PYTHONPYCACHEPREFIX"

echo "ci-check: compileall"
python3 -m compileall -q demo tests scripts/assert-reports.py

echo "ci-check: unittest"
python3 -m unittest discover -s tests -t . -q

echo "ci-check: bash -n"
bash -n scripts/wait-healthy.sh
bash -n scripts/hooks/ci-check.sh
bash -n scripts/install-docker-cli.sh
bash -n scripts/refresh-evidence.sh

echo "ci-check: required files"
test -f README.md
test -f PINNED_VERSIONS.txt
test -f NOTICE
test -f docs/COVERAGE.md
test -f docs/IMAGE-PIN-POLICY.md
test -f demo/scenarios/ga4gh_drs_wes.py
test -f demo/scenarios/stac_eo_search.py
test -f demo/scenarios/bids_app_qc.py
test -f fixtures/bids/minimal/dataset_description.json
test -f tests/test_http.py

echo "ci-check: pin consistency"
PIN="$(sed -n 's/^Synaptic-Core-ref=//p' PINNED_VERSIONS.txt)"
PG="$(sed -n 's/^postgres-image=//p' PINNED_VERSIONS.txt)"
test -n "$PIN"
grep -q "$PIN" Dockerfile
grep -q "$PIN" docker-compose.yml
grep -q "$PG" docker-compose.yml
AMD="$(sed -n 's/^docker-cli-sha256-amd64=//p' PINNED_VERSIONS.txt)"
ARM="$(sed -n 's/^docker-cli-sha256-arm64=//p' PINNED_VERSIONS.txt)"
grep -q "$AMD" Dockerfile
grep -q "$ARM" Dockerfile
grep -q "$AMD" Dockerfile.sibling
grep -q "$ARM" Dockerfile.sibling

echo "ci-check: OK"
