from pathlib import Path

import pymupdf
import pytest

from chunker.config import ChunkerConfig
from chunker.loaders import LoadedDocument, load_document

REAL_PDF = (
    Path(__file__).resolve().parents[2]
    / ".sddw"
    / "chunker"
    / "test_fixture_agentic_rag.pdf"
)


def _make_pdf(path: Path, texts: list[str | None]) -> None:
    """Build a small multi-page PDF.

    A ``None`` entry produces a text-free page (a drawn rectangle, no text
    layer) to exercise the empty-text path.
    """
    doc = pymupdf.open()
    for text in texts:
        page = doc.new_page()
        if text is None:
            page.draw_rect(pymupdf.Rect(72, 72, 300, 300), fill=(0, 0, 1))
        else:
            page.insert_text((72, 100), text)
    doc.save(str(path))
    doc.close()


@pytest.fixture
def config(tmp_path: Path) -> ChunkerConfig:
    return ChunkerConfig(output_dir=str(tmp_path / "out"))


class TestLoadPdf:
    def test_returns_pages_in_document_order(self, tmp_path, config):
        pdf = tmp_path / "doc.pdf"
        _make_pdf(pdf, ["Alpha page one", "Beta page two", "Gamma page three"])

        loaded = load_document(str(pdf), config)

        assert isinstance(loaded, LoadedDocument)
        assert loaded.source_text is None
        assert loaded.pages is not None
        assert [p.number for p in loaded.pages] == [1, 2, 3]
        assert "Alpha" in loaded.pages[0].text
        assert "Gamma" in loaded.pages[2].text

    def test_single_page_pdf(self, tmp_path, config):
        pdf = tmp_path / "single.pdf"
        _make_pdf(pdf, ["Only page"])

        loaded = load_document(str(pdf), config)

        assert loaded.pages is not None
        assert len(loaded.pages) == 1
        assert loaded.pages[0].number == 1

    def test_writes_png_per_page(self, tmp_path, config):
        pdf = tmp_path / "doc.pdf"
        _make_pdf(pdf, ["one", "two"])

        loaded = load_document(str(pdf), config)

        pages_dir = Path(config.output_dir) / "pages"
        for page in loaded.pages:
            assert Path(page.image_path).is_absolute()
            assert Path(page.image_path).exists()
            assert Path(page.image_path).parent == pages_dir
        assert (pages_dir / "page-0001.png").exists()
        assert (pages_dir / "page-0002.png").exists()

    def test_empty_text_page_tolerated(self, tmp_path, config):
        pdf = tmp_path / "with_blank.pdf"
        _make_pdf(pdf, ["has text", None])

        loaded = load_document(str(pdf), config)

        empty_page = loaded.pages[1]
        assert empty_page.text == ""
        assert Path(empty_page.image_path).exists()

    def test_dpi_controls_render_resolution(self, tmp_path):
        pdf = tmp_path / "doc.pdf"
        _make_pdf(pdf, ["resolution test"])

        low = ChunkerConfig(output_dir=str(tmp_path / "low"), pdf_dpi=72)
        high = ChunkerConfig(output_dir=str(tmp_path / "high"), pdf_dpi=144)
        low_doc = load_document(str(pdf), low)
        high_doc = load_document(str(pdf), high)

        low_w = pymupdf.Pixmap(low_doc.pages[0].image_path).width
        high_w = pymupdf.Pixmap(high_doc.pages[0].image_path).width
        assert high_w == pytest.approx(low_w * 2, abs=2)

    def test_missing_pdf_raises_file_not_found(self, tmp_path, config):
        with pytest.raises(FileNotFoundError, match="missing.pdf"):
            load_document(str(tmp_path / "missing.pdf"), config)

    def test_corrupt_pdf_raises_value_error(self, tmp_path, config):
        bad = tmp_path / "corrupt.pdf"
        bad.write_bytes(b"%PDF-1.4 not actually a pdf")

        with pytest.raises(ValueError, match="corrupt.pdf"):
            load_document(str(bad), config)


class TestLoadText:
    def test_txt_returns_source_text(self, tmp_path, config):
        txt = tmp_path / "doc.txt"
        txt.write_text("Plain text body.")

        loaded = load_document(str(txt), config)

        assert loaded.source_text == "Plain text body."
        assert loaded.pages is None
        assert loaded.document_id == "doc"

    def test_md_treated_as_text(self, tmp_path, config):
        md = tmp_path / "notes.md"
        md.write_text("# Heading\n\nBody.")

        loaded = load_document(str(md), config)

        assert loaded.pages is None
        assert loaded.source_text == "# Heading\n\nBody."

    def test_missing_text_file_raises(self, tmp_path, config):
        with pytest.raises(FileNotFoundError):
            load_document(str(tmp_path / "nope.txt"), config)


@pytest.mark.skipif(not REAL_PDF.exists(), reason="real PDF fixture not present")
class TestLoadRealFixture:
    def test_loads_real_multipage_pdf(self, tmp_path):
        config = ChunkerConfig(output_dir=str(tmp_path / "out"), pdf_dpi=72)

        loaded = load_document(str(REAL_PDF), config)

        assert loaded.source_text is None
        assert loaded.pages is not None
        assert len(loaded.pages) >= 1
        numbers = [p.number for p in loaded.pages]
        assert numbers == list(range(1, len(loaded.pages) + 1))
        for page in loaded.pages:
            assert Path(page.image_path).exists()
