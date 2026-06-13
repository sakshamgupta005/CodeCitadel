from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)


class GithubImportRequest(BaseModel):
    owner: str = Field(..., min_length=1, examples=["owner"])
    repo: str = Field(..., min_length=1, examples=["repo"])


class ImportResponse(BaseModel):
    imported_count: int
    indexed_count: int
    index_name: str
    job_id: str | None = None
    import_id: str | None = None
    message: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["Why is checkout slow?"])
    top_k: int = Field(default=10, ge=1, le=25)


class SearchResultItem(BaseModel):
    id: str
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["Why was checkout rewritten?"])
    top_k: int = Field(default=10, ge=1, le=25)


class Source(BaseModel):
    source: str
    type: str
    url: str | None = None
    id: str | None = None
    citation: str | None = None
    title: str | None = None
    repo: str | None = None
    score: float | None = None
    snippet: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class ErrorResponse(BaseModel):
    detail: str
    error_type: str | None = None


class ImportStatus(BaseModel):
    import_id: str
    source: str
    status: str
    imported_count: int = 0
    indexed_count: int = 0
    index_name: str
    job_id: str | None = None
    repo: str | None = None
    filename: str | None = None
    message: str
    error: str | None = None
    started_at: str
    finished_at: str | None = None


class ImportStatusResponse(BaseModel):
    active_imports: int
    last_import: ImportStatus | None = None
    imports: list[ImportStatus]


class RepositoryStats(BaseModel):
    repo: str
    total_documents: int
    issues: int = 0
    pull_requests: int = 0
    commits: int = 0
    last_import_id: str | None = None
    last_import_status: str | None = None


class RepositoryStatsResponse(BaseModel):
    repositories: list[RepositoryStats]


def clean_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        cleaned[str(key)] = str(value)
    return cleaned
