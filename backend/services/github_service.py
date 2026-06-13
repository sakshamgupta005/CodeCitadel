from __future__ import annotations

import logging
from typing import Any

import requests

from models.schemas import KnowledgeDocument, clean_metadata
from services.config import get_settings
from services.exceptions import ExternalServiceError


logger = logging.getLogger(__name__)


class GitHubService:
    base_url = "https://api.github.com"

    def __init__(self) -> None:
        settings = get_settings()
        self.max_pages = settings.github_max_pages
        self.timeout = settings.github_timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "company-brain-mvp",
            }
        )
        if settings.github_token:
            self.session.headers["Authorization"] = f"Bearer {settings.github_token}"

    def import_repository(self, owner: str, repo: str) -> list[KnowledgeDocument]:
        logger.info("Importing GitHub repository %s/%s", owner, repo)
        issues = self._fetch_issues(owner, repo)
        prs = self._fetch_pull_requests(owner, repo)
        commits = self._fetch_commits(owner, repo)
        documents = [*issues, *prs, *commits]
        logger.info("Normalized %s GitHub documents from %s/%s", len(documents), owner, repo)
        return documents

    def _fetch_issues(self, owner: str, repo: str) -> list[KnowledgeDocument]:
        items = self._fetch_paginated(
            f"/repos/{owner}/{repo}/issues",
            params={"state": "all", "per_page": 100},
        )
        issues = [item for item in items if "pull_request" not in item]
        return [self._normalize_issue(owner, repo, issue) for issue in issues]

    def _fetch_pull_requests(self, owner: str, repo: str) -> list[KnowledgeDocument]:
        pulls = self._fetch_paginated(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": "all", "per_page": 100},
        )
        return [self._normalize_pull_request(owner, repo, pull_request) for pull_request in pulls]

    def _fetch_commits(self, owner: str, repo: str) -> list[KnowledgeDocument]:
        commits = self._fetch_paginated(
            f"/repos/{owner}/{repo}/commits",
            params={"per_page": 100},
        )
        return [self._normalize_commit(owner, repo, commit) for commit in commits]

    def _fetch_paginated(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        url = f"{self.base_url}{path}"

        for page in range(1, self.max_pages + 1):
            request_params = {**params, "page": page}
            response = self.session.get(url, params=request_params, timeout=self.timeout)
            if response.status_code >= 400:
                self._raise_github_error(response)
            page_items = response.json()
            if not isinstance(page_items, list):
                raise ExternalServiceError("GitHub returned an unexpected response shape.")
            results.extend(page_items)
            if len(page_items) < int(params.get("per_page", 100)):
                break

        return results

    @staticmethod
    def _raise_github_error(response: requests.Response) -> None:
        try:
            message = response.json().get("message", response.text)
        except ValueError:
            message = response.text
        raise ExternalServiceError(f"GitHub API error {response.status_code}: {message}")

    @staticmethod
    def _normalize_issue(owner: str, repo: str, issue: dict[str, Any]) -> KnowledgeDocument:
        labels = ", ".join(label.get("name", "") for label in issue.get("labels", []))
        number = issue.get("number")
        title = issue.get("title") or ""
        body = issue.get("body") or ""
        text = "\n".join(
            part
            for part in [
                f"GitHub issue #{number}: {title}",
                f"State: {issue.get('state', '')}",
                f"Labels: {labels}" if labels else "",
                body,
            ]
            if part
        )
        metadata = clean_metadata(
            {
                "source": "github",
                "type": "issue",
                "repo": f"{owner}/{repo}",
                "url": issue.get("html_url"),
                "author": GitHubService._user_login(issue.get("user")),
                "created_at": issue.get("created_at"),
                "state": issue.get("state"),
                "number": number,
                "title": title,
            }
        )
        return KnowledgeDocument(
            id=f"github:{owner}/{repo}:issue:{number}",
            text=text,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_pull_request(
        owner: str,
        repo: str,
        pull_request: dict[str, Any],
    ) -> KnowledgeDocument:
        number = pull_request.get("number")
        title = pull_request.get("title") or ""
        body = pull_request.get("body") or ""
        merged = "yes" if pull_request.get("merged_at") else "no"
        base = (pull_request.get("base") or {}).get("ref", "")
        head = (pull_request.get("head") or {}).get("ref", "")
        text = "\n".join(
            part
            for part in [
                f"GitHub pull request #{number}: {title}",
                f"State: {pull_request.get('state', '')}",
                f"Merged: {merged}",
                f"Branch: {head} -> {base}" if base or head else "",
                body,
            ]
            if part
        )
        metadata = clean_metadata(
            {
                "source": "github",
                "type": "pr",
                "repo": f"{owner}/{repo}",
                "url": pull_request.get("html_url"),
                "author": GitHubService._user_login(pull_request.get("user")),
                "created_at": pull_request.get("created_at"),
                "state": pull_request.get("state"),
                "number": number,
                "title": title,
                "merged": merged,
            }
        )
        return KnowledgeDocument(
            id=f"github:{owner}/{repo}:pr:{number}",
            text=text,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_commit(owner: str, repo: str, commit: dict[str, Any]) -> KnowledgeDocument:
        sha = commit.get("sha", "")
        short_sha = sha[:12]
        commit_body = commit.get("commit") or {}
        author = commit_body.get("author") or {}
        message = commit_body.get("message") or ""
        first_line = message.splitlines()[0] if message else short_sha
        text = "\n".join(
            part
            for part in [
                f"GitHub commit {short_sha}: {first_line}",
                f"Author: {author.get('name', '')}" if author.get("name") else "",
                message,
            ]
            if part
        )
        metadata = clean_metadata(
            {
                "source": "github",
                "type": "commit",
                "repo": f"{owner}/{repo}",
                "url": commit.get("html_url"),
                "author": GitHubService._user_login(commit.get("author")) or author.get("name"),
                "created_at": author.get("date"),
                "sha": sha,
                "title": first_line,
            }
        )
        return KnowledgeDocument(
            id=f"github:{owner}/{repo}:commit:{sha}",
            text=text,
            metadata=metadata,
        )

    @staticmethod
    def _user_login(user: dict[str, Any] | None) -> str | None:
        if not user:
            return None
        return user.get("login")
