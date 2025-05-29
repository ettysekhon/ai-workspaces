.PHONY: format lint ci clean start

format:
	uv run black .
	uv run ruff check . --fix

lint:
	uv run ruff check .

ci: lint

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

start:
	docker compose up --build
