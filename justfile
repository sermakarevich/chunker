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

# Process a PDF directly -- no lossy pdftotext pre-pass. `model` must be vision-capable.
run-pdf input="output/ai_report_2026/ai_index_report_2026.pdf" model="gemma4:latest" output="output/ai_report_2026/":
    just run {{ input }} {{ model }} {{ output }}

run-fixture model="gemma4:latest":
    just run-pdf output/ai_report_2026/ai_index_report_2026.pdf {{ model }} output/ai_report_2026/
