"""Claude API generation from retrieved chunks."""

from __future__ import annotations

import anthropic

from r2.rag.config import RAGConfig, get_config
from r2.rag.generation.prompts import TEMPLATES, format_context
from r2.rag.retrieval.search import SearchResult


def generate(
    query: str,
    results: list[SearchResult],
    prompt_type: str = "synthesis",
    config: RAGConfig | None = None,
) -> str:
    """Generate a synthesis from search results using Claude API."""
    if config is None:
        config = get_config()

    if not config.anthropic_api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Add it to .env or set RAG_ANTHROPIC_API_KEY."
        )

    template = TEMPLATES.get(prompt_type)
    if template is None:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown prompt type '{prompt_type}'. Available: {available}")

    context = format_context(results)
    prompt = template.format(query=query, context=context)

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    message = client.messages.create(
        model=config.generation_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
