.PHONY: dev backend frontend test lint install

install:
	pip install -e ".[dev]"
	cd frontend && npm install

backend:
	uvicorn api.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@make backend &
	@sleep 2
	@make frontend

test:
	pytest tests/ -v

lint:
	ruff check ml2/ api/ tests/
	cd frontend && npx tsc --noEmit
