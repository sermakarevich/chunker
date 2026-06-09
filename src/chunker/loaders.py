from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from chunker.config import ChunkerConfig
from chunker.models import Page

logger = logging.getLogger(__name__)


@dataclass
class LoadedDocument:
    """Result of loading an input file.

    Exactly one of ``source_text`` (text mode) or ``pages`` (pdf mode) is set;
    the other is ``None``. Mode is discriminated by ``pages is not None``.
    """

    document_id: str
    source_text: str | None = None
    pages: list[Page] | None = None


def load_document(path: str, config: ChunkerConfig) -> LoadedDocument:
    """Load an input file, dispatching on its suffix.

    ``.pdf`` files are split into rendered pages (pdf mode); every other suffix
    is read as plain text (text mode), preserving the pre-feature behavior.
    Raises a clear, actionable error on a missing or unreadable input and never
    returns a partially built document.
    """
    document_id = Path(path).stem
    if path.lower().endswith(".pdf"):
        return _load_pdf(path, document_id, config)
    return _load_text(path, document_id)


def _load_text(path: str, document_id: str) -> LoadedDocument:
    text = Path(path).read_text()
    return LoadedDocument(document_id=document_id, source_text=text, pages=None)


def _load_pdf(path: str, document_id: str, config: ChunkerConfig) -> LoadedDocument:
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF not found: {path}")

    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001 - re-raised as a clear ValueError
        raise ValueError(f"Failed to open PDF {path!r}: {exc}") from exc

    pages_dir = os.path.join(config.output_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    zoom = config.pdf_dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)

    pages: list[Page] = []
    try:
        for index in range(doc.page_count):
            page = doc.load_page(index)
            text = page.get_text()
            number = index + 1
            image_path = os.path.abspath(
                os.path.join(pages_dir, f"page-{number:04d}.{config.image_format}")
            )
            page.get_pixmap(matrix=matrix).save(image_path)
            pages.append(Page(number=number, text=text, image_path=image_path))
    finally:
        doc.close()

    logger.info("Loaded PDF %s: %d page(s) at %d DPI", path, len(pages), config.pdf_dpi)
    return LoadedDocument(document_id=document_id, source_text=None, pages=pages)
