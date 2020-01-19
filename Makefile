.PHONY: init
init:
	poetry install

.PHONY: test
test:
	poetry run pytest --cov=cmdlib tests/ --capture=no --quiet
