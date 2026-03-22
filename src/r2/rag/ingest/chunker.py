"""Text chunking with section detection and metadata.

Supports both English and Japanese (CJK) text.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

from r2.rag.ingest.pdf import PageText, TextBlock


def _is_cjk_char(c: str) -> bool:
    """Check if a character is CJK (Chinese/Japanese/Korean)."""
    cp = ord(c)
    return (
        (0x4E00 <= cp <= 0x9FFF)       # CJK Unified Ideographs
        or (0x3040 <= cp <= 0x309F)     # Hiragana
        or (0x30A0 <= cp <= 0x30FF)     # Katakana
        or (0x3400 <= cp <= 0x4DBF)     # CJK Extension A
        or (0xFF66 <= cp <= 0xFF9F)     # Halfwidth Katakana
        or (0x20000 <= cp <= 0x2A6DF)   # CJK Extension B
    )


@dataclass
class ChunkMetadata:
    citekey: str
    author: str
    title: str
    year: str
    start_page: int
    end_page: int
    section: str
    chunk_idx: int


@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata


# Approximate tokens: words * 1.3 for Latin text, ~0.7 tokens per CJK char
_TOKENS_PER_WORD = 1.3
_TOKENS_PER_CJK_CHAR = 0.7

_REFERENCES_RE = re.compile(
    r"^(references|bibliography|works cited|literature cited"
    r"|参考文献|引用文献|文献|文献一覧|引用・参考文献)\s*$",
    re.IGNORECASE,
)


def _estimate_tokens(text: str) -> int:
    """Estimate token count, handling both Latin (space-separated) and CJK text."""
    cjk_count = sum(1 for c in text if _is_cjk_char(c))
    if cjk_count == 0:
        return int(len(text.split()) * _TOKENS_PER_WORD)
    # Mixed or pure CJK: count CJK chars separately + Latin words
    latin_parts = re.sub(r'[\u3000-\u9FFF\u30A0-\u30FF\u3040-\u309F]+', ' ', text)
    latin_words = len(latin_parts.split())
    return int(latin_words * _TOKENS_PER_WORD + cjk_count * _TOKENS_PER_CJK_CHAR)


def _detect_headers(pages: list[PageText]) -> dict[int, list[tuple[str, int]]]:
    """Detect section headers by font-size jumps.

    Returns {page_num: [(header_text, block_idx), ...]}.
    """
    # Collect all font sizes to compute median
    all_sizes: list[float] = []
    for page in pages:
        for block in page.blocks:
            # Skip very short blocks for median; use char count for CJK
            if len(block.text) > 10:
                all_sizes.append(block.font_size)

    if not all_sizes:
        return {}

    median_size = statistics.median(all_sizes)
    threshold = median_size + 1.5  # slightly relaxed from plan's +2

    headers: dict[int, list[tuple[str, int]]] = {}
    for page in pages:
        page_headers = []
        for i, block in enumerate(page.blocks):
            text = block.text.strip()
            # For CJK text, use character count instead of word count
            cjk_chars = sum(1 for c in text if _is_cjk_char(c))
            if cjk_chars > 0:
                is_short = len(text) < 60
            else:
                is_short = len(text) < 200 and len(text.split()) < 20
            if block.font_size >= threshold and is_short:
                page_headers.append((text, i))
        if page_headers:
            headers[page.page_num] = page_headers

    return headers


def _is_header_footer(block: TextBlock, page_height: float) -> bool:
    """Check if block is in top/bottom 5% of page (likely header/footer)."""
    _, y0, _, y1 = block.bbox
    top_margin = page_height * 0.05
    bottom_margin = page_height * 0.95
    return y1 < top_margin or y0 > bottom_margin


def _split_into_sections(pages: list[PageText]) -> list[tuple[str, str, int, int]]:
    """Split pages into sections: [(section_name, text, start_page, end_page), ...]."""
    headers = _detect_headers(pages)

    sections: list[tuple[str, str, int, int]] = []
    current_section = "Introduction"
    current_text_parts: list[str] = []
    current_start_page = 1
    in_references = False

    for page in pages:
        page_headers = dict(headers.get(page.page_num, []))  # text -> block_idx

        for i, block in enumerate(page.blocks):
            # Skip if it's a detected header — start new section
            if i in page_headers.values():
                header_text = block.text.strip()

                # Check if we've hit the references section
                if _REFERENCES_RE.match(header_text):
                    in_references = True
                    # Save current section
                    if current_text_parts:
                        sections.append((
                            current_section,
                            "\n".join(current_text_parts),
                            current_start_page,
                            page.page_num,
                        ))
                        current_text_parts = []
                    break  # skip rest of this and subsequent pages

                # Save previous section
                if current_text_parts:
                    sections.append((
                        current_section,
                        "\n".join(current_text_parts),
                        current_start_page,
                        page.page_num - 1 if page.page_num > 1 else 1,
                    ))
                    current_text_parts = []

                current_section = header_text
                current_start_page = page.page_num
                continue

            if in_references:
                break

            current_text_parts.append(block.text)

        if in_references:
            break

    # Final section
    if current_text_parts and not in_references:
        last_page = pages[-1].page_num if pages else 1
        sections.append((
            current_section,
            "\n".join(current_text_parts),
            current_start_page,
            last_page,
        ))

    return sections


def _chunk_text(text: str, target_tokens: int, overlap_tokens: int) -> list[str]:
    """Split text into chunks at paragraph/sentence boundaries."""
    if _estimate_tokens(text) <= target_tokens:
        return [text] if text.strip() else []

    # Split by paragraphs first
    paragraphs = re.split(r"\n\s*\n|\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks: list[str] = []
    current_parts: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = _estimate_tokens(para)

        if current_tokens + para_tokens > target_tokens and current_parts:
            chunks.append("\n".join(current_parts))
            # Overlap: keep last part if it fits
            overlap_parts: list[str] = []
            overlap_t = 0
            for p in reversed(current_parts):
                pt = _estimate_tokens(p)
                if overlap_t + pt <= overlap_tokens:
                    overlap_parts.insert(0, p)
                    overlap_t += pt
                else:
                    break
            current_parts = overlap_parts
            current_tokens = overlap_t

        # If a single paragraph exceeds target, split by sentences
        # Handles English (.!?) and Japanese (。！？) sentence endings
        if para_tokens > target_tokens:
            sentences = re.split(r"(?<=[.!?])\s+|(?<=[。！？])", para)
            for sent in sentences:
                sent_tokens = _estimate_tokens(sent)
                if current_tokens + sent_tokens > target_tokens and current_parts:
                    chunks.append("\n".join(current_parts))
                    overlap_parts = []
                    overlap_t = 0
                    for p in reversed(current_parts):
                        pt = _estimate_tokens(p)
                        if overlap_t + pt <= overlap_tokens:
                            overlap_parts.insert(0, p)
                            overlap_t += pt
                        else:
                            break
                    current_parts = overlap_parts
                    current_tokens = overlap_t
                current_parts.append(sent)
                current_tokens += sent_tokens
        else:
            current_parts.append(para)
            current_tokens += para_tokens

    if current_parts:
        chunks.append("\n".join(current_parts))

    return chunks


def chunk_document(
    pages: list[PageText],
    citekey: str,
    author: str,
    title: str,
    year: str,
    target_tokens: int = 800,
    overlap_tokens: int = 100,
) -> list[Chunk]:
    """Chunk a document into pieces with metadata."""
    sections = _split_into_sections(pages)

    chunks: list[Chunk] = []
    chunk_idx = 0

    for section_name, section_text, start_page, end_page in sections:
        text_chunks = _chunk_text(section_text, target_tokens, overlap_tokens)

        for text in text_chunks:
            if not text.strip():
                continue
            chunks.append(Chunk(
                text=text,
                metadata=ChunkMetadata(
                    citekey=citekey,
                    author=author,
                    title=title,
                    year=year,
                    start_page=start_page,
                    end_page=end_page,
                    section=section_name,
                    chunk_idx=chunk_idx,
                ),
            ))
            chunk_idx += 1

    return chunks
