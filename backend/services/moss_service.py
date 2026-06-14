from __future__ import annotations

import asyncio
import logging
from typing import Sequence

from moss import DocumentInfo, MossClient, MutationOptions, QueryOptions

from models.schemas import KnowledgeDocument, SearchResultItem
from services.config import get_settings
from services.exceptions import ConfigurationError, ExternalServiceError, InputValidationError


logger = logging.getLogger(__name__)


class MossService:
    def __init__(self) -> None:
        self._client: MossClient | None = None
        self._loaded_index = False

    @property
    def index_name(self) -> str:
        return get_settings().moss_index_name

    @property
    def client(self) -> MossClient:
        if self._client is None:
            settings = get_settings()
            if not settings.moss_project_id or not settings.moss_project_key:
                raise ConfigurationError(
                    "Moss is not configured. Set MOSS_PROJECT_ID and MOSS_PROJECT_KEY in backend/.env."
                )
            self._client = MossClient(settings.moss_project_id, settings.moss_project_key)
        return self._client

    async def create_index_if_needed(
        self,
        documents: Sequence[KnowledgeDocument] | None = None,
    ) -> object | None:
        if await self._index_exists():
            return None
        if not documents:
            raise InputErrorForEmptyIndex(
                "No documents were available to index. Upload product knowledge first."
            )

        settings = get_settings()
        logger.info("Creating Moss index %s with %s documents", self.index_name, len(documents))
        result = await self.client.create_index(
            self.index_name,
            self._to_moss_documents(documents),
            model_id=settings.moss_model_id,
        )
        await self._wait_for_job(getattr(result, "job_id", None))
        await self._load_index_best_effort(force=True)
        return result

    async def add_documents(self, documents: Sequence[KnowledgeDocument]) -> tuple[int, str | None]:
        if not documents:
            return 0, None

        create_result = await self.create_index_if_needed(documents)
        if create_result is not None:
            return len(documents), getattr(create_result, "job_id", None)

        logger.info("Upserting %s documents into Moss index %s", len(documents), self.index_name)
        result = await self.client.add_docs(
            self.index_name,
            self._to_moss_documents(documents),
            MutationOptions(upsert=True),
        )
        await self._wait_for_job(getattr(result, "job_id", None))
        await self._load_index_best_effort(force=True)
        return len(documents), getattr(result, "job_id", None)

    async def search_documents(self, query: str, top_k: int = 10) -> list[SearchResultItem]:
        await self._load_index_best_effort()
        settings = get_settings()
        logger.info("Searching Moss index %s for query=%r", self.index_name, query)
        try:
            result = await self.client.query(
                self.index_name,
                query,
                QueryOptions(top_k=top_k, alpha=settings.moss_search_alpha),
            )
        except Exception as exc:
            raise ExternalServiceError(f"Moss search failed: {exc}") from exc

        return [self._to_search_item(document) for document in getattr(result, "docs", [])]

    async def _index_exists(self) -> bool:
        try:
            indexes = await self.client.list_indexes()
        except Exception as exc:
            raise ExternalServiceError(f"Could not list Moss indexes: {exc}") from exc
        return any(getattr(index, "name", None) == self.index_name for index in indexes)

    async def _wait_for_job(self, job_id: str | None) -> None:
        if not job_id:
            return

        timeout_seconds = get_settings().moss_wait_for_index_seconds
        if timeout_seconds <= 0:
            return

        deadline = asyncio.get_running_loop().time() + timeout_seconds
        while True:
            status_response = await self.client.get_job_status(job_id)
            status = self._status_value(getattr(status_response, "status", "")).lower()
            if status in {"completed", "ready", "succeeded", "success"}:
                return
            if status in {"failed", "error"}:
                error = getattr(status_response, "error", None) or "unknown error"
                raise ExternalServiceError(f"Moss indexing job failed: {error}")
            if asyncio.get_running_loop().time() >= deadline:
                logger.warning("Timed out waiting for Moss job %s; continuing anyway", job_id)
                return
            await asyncio.sleep(1.0)

    async def _load_index_best_effort(self, force: bool = False) -> None:
        if self._loaded_index and not force:
            return
        try:
            await self.client.load_index(self.index_name)
            self._loaded_index = True
            logger.info("Loaded Moss index %s for local search", self.index_name)
        except Exception as exc:
            self._loaded_index = False
            logger.warning("Could not load Moss index locally; cloud query fallback may be used: %s", exc)

    @staticmethod
    def _to_moss_documents(documents: Sequence[KnowledgeDocument]) -> list[DocumentInfo]:
        return [
            DocumentInfo(id=document.id, text=document.text, metadata=document.metadata)
            for document in documents
        ]

    @staticmethod
    def _to_search_item(document: object) -> SearchResultItem:
        metadata = getattr(document, "metadata", None) or {}
        return SearchResultItem(
            id=str(getattr(document, "id", "")),
            text=str(getattr(document, "text", "")),
            metadata={str(key): str(value) for key, value in metadata.items()},
            score=float(getattr(document, "score", 0.0) or 0.0),
        )

    @staticmethod
    def _status_value(status: object) -> str:
        value = getattr(status, "value", status)
        return str(value)


class InputErrorForEmptyIndex(InputValidationError):
    pass
