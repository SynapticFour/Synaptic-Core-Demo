# Makefile — Synaptic-Core-Demo

.PHONY: help up up-sibling down reset wait-healthy \
	demo-ga4gh demo-stac demo-bids demo-all smoke-syntax

SC_BASE_URL ?= http://127.0.0.1:8080
export SC_BASE_URL

help:
	@echo "Synaptic-Core-Demo"
	@echo "  make up-sibling   Choice A stack from ../Synaptic-Core (dev)"
	@echo "  make up           Choice A stack from pinned Synaptic-Core-ref"
	@echo "  make down/reset   Stop / wipe volumes"
	@echo "  make demo-ga4gh   Genomics: DRS → TRS → WES/TES"
	@echo "  make demo-stac    EO: STAC search → process task"
	@echo "  make demo-bids    Neuroimaging: BIDS index → QC-style task"
	@echo "  make demo-all     Run all three demos"
	@echo "  make smoke-syntax CI parity (no Docker stack)"

up:
	docker compose up --build -d
	@$(MAKE) wait-healthy

up-sibling:
	docker compose -f docker-compose.yml -f docker-compose.sibling.yml up --build -d
	@$(MAKE) wait-healthy

down:
	docker compose down --remove-orphans

reset:
	docker compose down -v --remove-orphans

wait-healthy:
	@chmod +x scripts/wait-healthy.sh
	./scripts/wait-healthy.sh "$(SC_BASE_URL)"

demo-ga4gh: wait-healthy
	@mkdir -p artifacts
	python3 demo/scenarios/ga4gh_drs_wes.py --base-url "$(SC_BASE_URL)" --out artifacts/ga4gh.json

demo-stac: wait-healthy
	@mkdir -p artifacts
	python3 demo/scenarios/stac_eo_search.py --base-url "$(SC_BASE_URL)" --out artifacts/stac.json

demo-bids: wait-healthy
	@mkdir -p artifacts
	python3 demo/scenarios/bids_app_qc.py --base-url "$(SC_BASE_URL)" --out artifacts/bids.json

demo-all: demo-ga4gh demo-stac demo-bids
	@echo "All demos OK — see artifacts/"

smoke-syntax:
	@chmod +x scripts/hooks/ci-check.sh
	./scripts/hooks/ci-check.sh
