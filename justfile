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

run-fixture model="gemma4:31b":
    pdftotext output/ai_report_2025/hai_ai_index_report_2025.pdf output/ai_report_2025/report.txt
    just run output/ai_report_2025/report.txt {{ model }} output/ai_report_2025/
