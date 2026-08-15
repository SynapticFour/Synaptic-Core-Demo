# Makefile — Synaptic-Core-Demo

.PHONY: help up up-sibling up-pinned down reset wait-healthy \
	demo-ga4gh demo-stac demo-bids demo-all smoke-syntax test evidence evidence-pack

PIN_FILE := PINNED_VERSIONS.txt
SYNAPTIC_CORE_REF := $(shell sed -n 's/^Synaptic-Core-ref=//p' $(PIN_FILE))
POSTGRES_IMAGE := $(shell sed -n 's/^postgres-image=//p' $(PIN_FILE))
DEMO_CONTAINER_IMAGE := $(shell sed -n 's/^demo-container-image=//p' $(PIN_FILE))
SC_BASE_URL ?= http://127.0.0.1:8080
export SYNAPTIC_CORE_REF POSTGRES_IMAGE DEMO_CONTAINER_IMAGE SC_BASE_URL

help:
	@echo "Synaptic-Core-Demo"
	@echo "  make up           Sibling Core if ../Synaptic-Core exists, else fail"
	@echo "  make up-sibling   Choice A stack from ../Synaptic-Core"
	@echo "  make up-pinned    Build from PINNED_VERSIONS Synaptic-Core-ref (private clone)"
	@echo "  make down/reset   Stop / wipe volumes"
	@echo "  make demo-ga4gh   DRS → TRS → WES/TES until COMPLETE"
	@echo "  make demo-stac    Fixture vs live STAC projection + TES COMPLETE"
	@echo "  make demo-bids    Ingest fixture → live /bids/participants + TES COMPLETE"
	@echo "  make demo-all     Run all three (fail-closed)"
	@echo "  make evidence     Re-run demo-all then copy artifacts → docs/evidence"
	@echo "  make evidence-pack Copy existing artifacts/ (stack must still be up)"
	@echo "  make test         Unit tests (no Docker)"
	@echo "  make smoke-syntax CI parity: syntax + unit tests + pin check"

up:
	@if [ ! -d ../Synaptic-Core ]; then \
		echo "ERROR: ../Synaptic-Core missing. Clone Core next to this repo and run make up-sibling,"; \
		echo "or use make up-pinned if you can read the private Synaptic-Core repo."; \
		exit 1; \
	fi
	@$(MAKE) up-sibling

up-sibling:
	docker compose -f docker-compose.yml -f docker-compose.sibling.yml up --build -d
	@$(MAKE) wait-healthy

up-pinned:
	docker compose up --build -d
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
	python3 scripts/assert-reports.py artifacts/ga4gh.json

demo-stac: wait-healthy
	@mkdir -p artifacts
	python3 demo/scenarios/stac_eo_search.py --base-url "$(SC_BASE_URL)" --out artifacts/stac.json
	python3 scripts/assert-reports.py artifacts/stac.json

demo-bids: wait-healthy
	@mkdir -p artifacts
	python3 demo/scenarios/bids_app_qc.py --base-url "$(SC_BASE_URL)" --out artifacts/bids.json
	python3 scripts/assert-reports.py artifacts/bids.json

demo-all: demo-ga4gh demo-stac demo-bids
	@echo "All demos COMPLETE — see artifacts/"

evidence: demo-all evidence-pack

evidence-pack:
	@chmod +x scripts/refresh-evidence.sh
	./scripts/refresh-evidence.sh

test:
	python3 -m unittest discover -s tests -t . -v

smoke-syntax:
	@chmod +x scripts/hooks/ci-check.sh
	./scripts/hooks/ci-check.sh
