default:
    @just --list

test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

run *args:
    uv run chunker {{args}}

run-fixture model="gemma4:latest":
    pdftotext .sddw/chunker/test_fixture_agentic_rag.pdf tests/fixtures/agentic_rag_full.txt
    uv run chunker run tests/fixtures/agentic_rag_full.txt --model {{model}} --output-dir .sddw/agentic_rag
