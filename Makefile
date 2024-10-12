PYTEST_ARGS :=

.PHONY: default
default: test

################################################################################
# Virtual environment.

.venv/updated: poetry.lock
	poetry install --sync && touch $@

.PHONY: lock
lock:
	poetry lock --no-update

.PHONY: venv
venv: .venv/updated


################################################################################
# Dev targets.

.PHONY: check-fmt
check-fmt: venv
	poetry run ruff format --check --quiet

.PHONY: check-types
check-types: venv
	poetry run mypy src && cat .mypy_report/linecount.txt
	poetry run mypy tests && cat .mypy_report/linecount.txt

.PHONY: lint
lint: venv
	poetry run ruff check --quiet

.PHONY: check
check: check-fmt lint check-types

.PHONY: test
test: venv
	poetry run pytest --cov=cmdlib --quiet $(PYTEST_ARGS) tests/

.PHONY: build
build: venv
	poetry build

.PHONY: publish
publish: venv
	poetry publish
