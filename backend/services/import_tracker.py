from __future__ import annotations

import logging
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from models.schemas import ImportStatus, KnowledgeDocument, RepositoryStats


logger = logging.getLogger(__name__)


class ImportTracker:
    def __init__(self) -> None:
        self._imports: dict[str, ImportStatus] = {}
        self._repo_stats: dict[str, RepositoryStats] = {}
        self._last_import_id: str | None = None
        self._lock = Lock()

    def start(self, source: str, index_name: str, repo: str | None = None, filename: str | None = None) -> str:
        import_id = str(uuid4())
        status = ImportStatus(
            import_id=import_id,
            source=source,
            status="running",
            index_name=index_name,
            repo=repo,
            filename=filename,
            message="Import started.",
            started_at=self._now(),
        )
        with self._lock:
            self._imports[import_id] = status
            self._last_import_id = import_id
        logger.info("Started %s import %s", source, import_id)
        return import_id

    def complete(
        self,
        import_id: str,
        documents: list[KnowledgeDocument],
        indexed_count: int,
        job_id: str | None,
        message: str,
    ) -> ImportStatus:
        with self._lock:
            status = self._imports[import_id]
            updated = status.model_copy(
                update={
                    "status": "completed",
                    "imported_count": len(documents),
                    "indexed_count": indexed_count,
                    "job_id": job_id,
                    "message": message,
                    "finished_at": self._now(),
                }
            )
            self._imports[import_id] = updated
            self._update_repo_stats(import_id, documents, updated.status)
        logger.info("Completed import %s with %s indexed documents", import_id, indexed_count)
        return updated

    def fail(self, import_id: str, error: str) -> ImportStatus | None:
        with self._lock:
            status = self._imports.get(import_id)
            if status is None:
                return None
            updated = status.model_copy(
                update={
                    "status": "failed",
                    "message": "Import failed.",
                    "error": error,
                    "finished_at": self._now(),
                }
            )
            self._imports[import_id] = updated
            if updated.repo:
                existing = self._repo_stats.get(updated.repo)
                if existing:
                    self._repo_stats[updated.repo] = existing.model_copy(
                        update={"last_import_id": import_id, "last_import_status": "failed"}
                    )
        logger.warning("Failed import %s: %s", import_id, error)
        return updated

    def list_imports(self) -> list[ImportStatus]:
        with self._lock:
            return sorted(self._imports.values(), key=lambda item: item.started_at, reverse=True)

    def last_import(self) -> ImportStatus | None:
        with self._lock:
            if self._last_import_id is None:
                return None
            return self._imports.get(self._last_import_id)

    def active_count(self) -> int:
        with self._lock:
            return sum(1 for status in self._imports.values() if status.status == "running")

    def repository_stats(self) -> list[RepositoryStats]:
        with self._lock:
            return sorted(self._repo_stats.values(), key=lambda item: item.repo)

    def _update_repo_stats(self, import_id: str, documents: list[KnowledgeDocument], status: str) -> None:
        repo_docs = [document for document in documents if document.metadata.get("source") == "github"]
        repos = sorted({document.metadata.get("repo", "") for document in repo_docs if document.metadata.get("repo")})

        for repo in repos:
            documents_for_repo = [document for document in repo_docs if document.metadata.get("repo") == repo]
            counts = {"issue": 0, "pr": 0, "commit": 0}
            for document in documents_for_repo:
                document_type = document.metadata.get("type", "")
                if document_type in counts:
                    counts[document_type] += 1

            existing = self._repo_stats.get(repo)
            previous_total = existing.total_documents if existing else 0
            self._repo_stats[repo] = RepositoryStats(
                repo=repo,
                total_documents=previous_total + len(documents_for_repo),
                issues=(existing.issues if existing else 0) + counts["issue"],
                pull_requests=(existing.pull_requests if existing else 0) + counts["pr"],
                commits=(existing.commits if existing else 0) + counts["commit"],
                last_import_id=import_id,
                last_import_status=status,
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()


import_tracker = ImportTracker()
