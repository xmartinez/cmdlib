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
	python3.7 -m venv .venv && \
	.venv/bin/python -m pip install --upgrade pip setuptools && \
	touch $@

.venv/updated: .venv/created poetry.lock
	poetry install && touch $@

.PHONY: venv
venv: .venv/updated


################################################################################
# Dev targets.

.PHONY: check-fmt
check-fmt: venv
	poetry run black --check --quiet .

.PHONY: check-types
check-types: venv
	poetry run mypy . && cat .mypy_report/linecount.txt

.PHONY: lint
lint: venv
	poetry run flake8 --exclude=.venv

.PHONY: check
check: check-fmt check-types lint

.PHONY: test
test: venv
	poetry run pytest --cov=cmdlib --quiet $(PYTEST_ARGS) tests/

.PHONY: build
build: venv
	poetry build

.PHONY: publish
publish: venv
	poetry publish
