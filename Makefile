PYTEST_ARGS :=

.PHONY: default
default: test

################################################################################
# Virtual environment.

poetry.lock: pyproject.toml
	poetry lock

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

.PHONY: check
check: venv
	poetry run mypy . && cat .mypy_report/linecount.txt

.PHONY: test
test: venv check
	poetry run pytest --cov=cmdlib --quiet $(PYTEST_ARGS) tests/

.PHONY: build
build: venv
	poetry build

.PHONY: publish
publish: venv
	poetry publish
