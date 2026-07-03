"""Construction de prompts RAG."""

from __future__ import annotations

from rag.schemas import RetrievedChunk
from rag.selectors import get_prompt_template


def build_context(chunks: list[RetrievedChunk]) -> str:
    """Assemble les chunks retrouvés en un bloc de contexte."""
    if not chunks:
        return ""
    parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        parts.append(f"[{index}] {chunk.text}")
    return "\n\n".join(parts)


def build_rag_messages(
    query: str,
    chunks: list[RetrievedChunk],
    *,
    template: str | None = None,
) -> list[dict[str, str]]:
    """Construit les messages pour completion (package inference)."""
    prompt_template = template or get_prompt_template()
    context = build_context(chunks)
    user_content = prompt_template.format(context=context, question=query)
    return [{"role": "user", "content": user_content}]
