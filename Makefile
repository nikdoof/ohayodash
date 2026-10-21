PYTHON_VERSION ?= $(shell cat .python-version)
RUFF_TARGET_VERSION = py$(subst .,,$(PYTHON_VERSION))

.PHONY: lint
lint:
	uv run --python $(PYTHON_VERSION) --dev ruff check --output-format=github --select=E9,F63,F7,F82 --target-version=$(RUFF_TARGET_VERSION) .
	uv run --python $(PYTHON_VERSION) --dev -m ruff check --output-format=github --target-version=$(RUFF_TARGET_VERSION) .
serve:
	uv run --dev -m flask --app ohayodash.app:app run
