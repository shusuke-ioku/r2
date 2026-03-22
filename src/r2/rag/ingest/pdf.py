"""PDF text extraction using PyMuPDF."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF


@dataclass
class TextBlock:
    text: str
    font_size: float
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1


@dataclass
class PageText:
    page_num: int
    text: str
    blocks: list[TextBlock] = field(default_factory=list)


def is_japanese(text: str) -> bool:
    """Check if text is predominantly Japanese (CJK characters)."""
    if not text:
        return False
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff"
              or "\u3040" <= c <= "\u309f"
              or "\u30a0" <= c <= "\u30ff")
    alpha = sum(1 for c in text if c.isalpha())
    if alpha == 0:
        return False
    return cjk / alpha > 0.3


def extract_pdf(pdf_path: Path, max_pages: int = 200) -> list[PageText]:
    """Extract text from PDF with block-level font information.

    Uses sort=True for reading-order in multi-column layouts.
    """
    doc = fitz.open(str(pdf_path))
    pages: list[PageText] = []

    for page_idx in range(min(len(doc), max_pages)):
        page = doc[page_idx]
        page_dict = page.get_text("dict", sort=True)
        page_height = page_dict.get("height", 792)

        blocks: list[TextBlock] = []
        full_text_parts: list[str] = []

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # text blocks only
                continue

            block_text_parts: list[str] = []
            font_sizes: list[float] = []

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        block_text_parts.append(text)
                        font_sizes.append(span.get("size", 10.0))

            if not block_text_parts:
                continue

            block_text = " ".join(block_text_parts)
            avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 10.0
            bbox = tuple(block["bbox"])

            blocks.append(TextBlock(
                text=block_text,
                font_size=avg_font_size,
                bbox=bbox,
            ))
            full_text_parts.append(block_text)

        pages.append(PageText(
            page_num=page_idx + 1,
            text="\n".join(full_text_parts),
            blocks=blocks,
        ))

    doc.close()
    return pages
