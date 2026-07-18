.PHONY: install run test db

install:
	python -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	python -m pytest -q

db:
	docker compose up -d
