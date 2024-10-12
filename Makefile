PYTEST_ARGS :=

.PHONY: default
default: test

################################################################################
# Virtual environment.

poetry.lock: pyproject.toml
	poetry lock && touch $@

# Manually create virtual environment, to ensure that we use a recent
# `pip` and `setuptools` version.
#
# See: https://github.com/python-poetry/poetry/issues/732
.venv/created:
	python3 -m venv .venv && \
	.venv/bin/python -m pip install --upgrade pip setuptools && \
	touch $@

.venv/updated: .venv/created poetry.lock
	poetry install && \
	scripts/fix-mypy-root-pth.sh cmdlib && \
	touch $@

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
