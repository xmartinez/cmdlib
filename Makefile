.PHONY: init
init:
	poetry env use python3.7 && poetry install

.PHONY: test
test:
	poetry run pytest --cov=cmdlib tests/ --capture=no --quiet

.PHONY: build
build:
	poetry build

.PHONY: publish
publish:
	poetry publish
