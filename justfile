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
    # pdftotext .sddw/chunker/test_fixture_agentic_rag.pdf tests/fixtures/agentic_rag_full.txt
    # pdftotext ./output/the_pragmatic_programmer/pragm.pdf ./output/the_pragmatic_programmer/the_pragmatic_programmer.txt
    pdftotext ./output/functional_programming_in_scala/Functional-Programming-in-Scala.pdf ./output/functional_programming_in_scala/functional_programming_in_scala.txt
    just run ./output/functional_programming_in_scala/functional_programming_in_scala.txt {{ model }}
