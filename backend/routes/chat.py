from __future__ import annotations

import logging

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse, SearchRequest, SearchResponse, Source
from services.llm_service import LLMService, NO_EVIDENCE_ANSWER
from services.moss_service import MossService


router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)

moss_service = MossService()
llm_service = LLMService()


@router.post("/search", response_model=SearchResponse)
async def search(payload: SearchRequest) -> SearchResponse:
    logger.info("Search requested query=%r top_k=%s", payload.query, payload.top_k)
    results = await moss_service.search_documents(query=payload.query, top_k=payload.top_k)
    logger.info("Search completed query=%r results=%s", payload.query, len(results))
    return SearchResponse(query=payload.query, results=results)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    logger.info("Chat requested query=%r top_k=%s", payload.query, payload.top_k)
    results = await moss_service.search_documents(query=payload.query, top_k=payload.top_k)
    answer = await llm_service.answer_from_context(query=payload.query, documents=results)
    sources = [] if answer == NO_EVIDENCE_ANSWER else _dedupe_sources(results)
    logger.info("Chat completed query=%r sources=%s no_evidence=%s", payload.query, len(sources), answer == NO_EVIDENCE_ANSWER)
    return ChatResponse(answer=answer, sources=sources)


def _dedupe_sources(results: list[object]) -> list[Source]:
    seen: set[tuple[str | None, str | None]] = set()
    sources: list[Source] = []

    for index, result in enumerate(results, start=1):
        metadata = getattr(result, "metadata", {}) or {}
        document_id = getattr(result, "id", None)
        source = metadata.get("source", "")
        source_type = metadata.get("type", "")
        url = metadata.get("url") or None
        key = (str(document_id) if document_id else None, url)
        if key in seen:
            continue
        seen.add(key)
        text = str(getattr(result, "text", "") or "")
        snippet = text[:240].replace("\n", " ").strip()
        sources.append(
            Source(
                source=source,
                type=source_type,
                url=url,
                id=str(document_id) if document_id else None,
                citation=f"[Source {index}]",
                title=metadata.get("title"),
                repo=metadata.get("repo"),
                score=getattr(result, "score", None),
                snippet=snippet,
            )
        )

    return sources
