.PHONY: up down install ingest api test lint eval
up:
	docker compose up -d
down:
	docker compose down
install:
	pip install -e ".[dev]"
ingest:
	python scripts/ingest.py --tickers AAPL MSFT NVDA --years 3
api:
	uvicorn filingsiq.api.main:app --reload
test:
	pytest
lint:
	ruff check src tests
eval:
	python -m filingsiq.evals.run_evals
