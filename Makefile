.PHONY: *

fmt:
	ruff format .

fmt-check:
	ruff format --check

install:
	pip install . '.[dev]' '.[test]'

lint:
	ruff check --select I
	ruff check

test-unit:
	pytest test

test-e2e:
	pytest e2e

type-check:
	pyright

ci: install fmt-check lint type-check test-unit test-e2e
