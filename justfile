default:
    @just --list

test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

run input="./output/the_pragmatic_programmer/the_pragmatic_programmer.txt" model="gemma4:latest" output="./output/functional_programming_in_scala/":
    #!/usr/bin/env bash
    set -euo pipefail
    output_dir="{{ output }}"
    if [ -z "$output_dir" ]; then
        output_dir=$(mktemp -d -t chunker-XXXXXX)
    fi
    echo "Output: $output_dir"
    uv run chunker run {{ input }} --model {{ model }} --output-dir "$output_dir"

run-fixture model="gemma4:latest":
    pdftotext output/opus47/Claude_Opus_4.7_System_Card.pdf output/opus47/opus47_system_card.txt
    just run output/opus47/opus47_system_card.txt {{ model }} output/opus47/
