from __future__ import annotations

import asyncio
import logging

from openai import OpenAI, OpenAIError

from models.schemas import SearchResultItem
from services.config import get_settings
from services.exceptions import ConfigurationError, ExternalServiceError


logger = logging.getLogger(__name__)

NO_EVIDENCE_ANSWER = "I could not find evidence in the indexed company knowledge."


class LLMService:
    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            settings = get_settings()
            if not settings.openai_api_key:
                raise ConfigurationError("OPENAI_API_KEY must be set.")
            self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    async def answer_from_context(self, query: str, documents: list[SearchResultItem]) -> str:
        if not documents:
            return NO_EVIDENCE_ANSWER

        settings = get_settings()
        prompt = self._build_prompt(query=query, documents=documents)
        logger.info("Generating answer with OpenAI model %s", settings.openai_model)

        try:
            response = await asyncio.to_thread(
                self.client.responses.create,
                model=settings.openai_model,
                instructions=self._instructions(),
                input=prompt,
            )
        except OpenAIError as exc:
            raise ExternalServiceError(f"OpenAI request failed: {exc}") from exc

        answer = getattr(response, "output_text", "") or ""
        return answer.strip() or NO_EVIDENCE_ANSWER

    @staticmethod
    def _instructions() -> str:
        return (
            "You are Company Brain, an organizational memory assistant. "
            "Answer strictly and only from the retrieved context supplied by the user. "
            f"If the context does not contain enough evidence, answer exactly: {NO_EVIDENCE_ANSWER} "
            "Do not use outside knowledge. Keep answers concise and cite evidence with source labels like [Source 1]."
        )

    @staticmethod
    def _build_prompt(query: str, documents: list[SearchResultItem]) -> str:
        max_context_chars = get_settings().max_context_chars
        sections: list[str] = []
        used_chars = 0

        for index, document in enumerate(documents, start=1):
            metadata = document.metadata
            section = (
                f"[Source {index}]\n"
                f"id: {document.id}\n"
                f"source: {metadata.get('source', '')}\n"
                f"type: {metadata.get('type', '')}\n"
                f"repo: {metadata.get('repo', '')}\n"
                f"url: {metadata.get('url', '')}\n"
                f"created_at: {metadata.get('created_at', '')}\n"
                f"text:\n{document.text}\n"
            )
            if used_chars + len(section) > max_context_chars:
                remaining = max_context_chars - used_chars
                if remaining > 500:
                    sections.append(section[:remaining])
                break
            sections.append(section)
            used_chars += len(section)

        context = "\n---\n".join(sections)
        return f"Question: {query}\n\nRetrieved context:\n{context}"
