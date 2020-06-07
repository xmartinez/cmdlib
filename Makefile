PYTEST_ARGS :=

.PHONY: init
init:
	poetry env use python3.7 && poetry install

.PHONY: test
test:
	poetry run pytest --cov=cmdlib --quiet $(PYTEST_ARGS) tests/

.PHONY: build
build:
	poetry build

.PHONY: publish
publish:
	poetry publish
