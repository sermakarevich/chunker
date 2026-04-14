from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def agentic_rag_text() -> str:
    return (FIXTURES_DIR / "agentic_rag_excerpt.txt").read_text()
