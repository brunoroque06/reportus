.PHONY: *

fmt:
	ruff format .

fmt-check:
	ruff format --check

install:
	pip install . --group dev

lint:
	ruff check --select I
	ruff check

test-unit:
	pytest test

test-e2e:
	pytest e2e

type-check:
	pyrefly check

ci: install fmt-check lint type-check test-unit test-e2e
