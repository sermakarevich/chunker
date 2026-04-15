default:
    @just --list

test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

run input="tests/fixtures/agentic_rag_full.txt" model="gemma4:latest" output="":
    #!/usr/bin/env bash
    set -euo pipefail
    output_dir="{{ output }}"
    if [ -z "$output_dir" ]; then
        output_dir=$(mktemp -d -t chunker-XXXXXX)
    fi
    echo "Output: $output_dir"
    uv run chunker run {{ input }} --model {{ model }} --output-dir "$output_dir"

run-fixture model="gemma4:latest":
    pdftotext .sddw/chunker/test_fixture_agentic_rag.pdf tests/fixtures/agentic_rag_full.txt
    just run tests/fixtures/agentic_rag_full.txt {{ model }}
