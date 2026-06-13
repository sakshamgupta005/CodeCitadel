from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from models.schemas import GithubImportRequest, ImportResponse, RepositoryStatsResponse
from services.github_service import GitHubService
from services.import_tracker import import_tracker
from services.moss_service import MossService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/github", tags=["github"])

github_service = GitHubService()
moss_service = MossService()


@router.post("/import", response_model=ImportResponse)
async def import_github_repository(payload: GithubImportRequest) -> ImportResponse:
    repo_name = f"{payload.owner}/{payload.repo}"
    import_id = import_tracker.start(source="github", index_name=moss_service.index_name, repo=repo_name)
    logger.info("GitHub import started for %s with import_id=%s", repo_name, import_id)
    try:
        documents = await run_in_threadpool(
            github_service.import_repository,
            payload.owner,
            payload.repo,
        )
        indexed_count, job_id = await moss_service.add_documents(documents)
    except Exception as exc:
        import_tracker.fail(import_id, str(exc))
        logger.exception("GitHub import failed for %s with import_id=%s", repo_name, import_id)
        raise

    message = f"Imported {indexed_count} GitHub documents from {repo_name}."
    import_tracker.complete(
        import_id=import_id,
        documents=documents,
        indexed_count=indexed_count,
        job_id=job_id,
        message=message,
    )
    logger.info("GitHub import completed for %s with import_id=%s", repo_name, import_id)
    return ImportResponse(
        imported_count=len(documents),
        indexed_count=indexed_count,
        index_name=moss_service.index_name,
        job_id=job_id,
        import_id=import_id,
        message=message,
    )


@router.get("/stats", response_model=RepositoryStatsResponse)
async def repository_stats() -> RepositoryStatsResponse:
    return RepositoryStatsResponse(repositories=import_tracker.repository_stats())
