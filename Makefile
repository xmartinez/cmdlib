.PHONY: init
init:
	poetry install

.PHONY: test
test:
	poetry run pytest --cov=cmdlib tests/ --capture=no --quiet

.PHONY: build
build:
	poetry build

.PHONY: publish
publish:
	poetry publish
