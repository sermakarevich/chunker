test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

run *args:
    uv run chunker {{args}}
