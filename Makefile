.PHONY: lint
lint:
	uv run --dev ruff check --output-format=github --select=E9,F63,F7,F82 --target-version=py39 .
	uv run --dev -m ruff check --output-format=github --target-version=py39 .
serve:
	uv run --dev -m flask --app ohayodash.app:app run