from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class PullRequestFile:
    filename: str
    status: str
    patch: str


class GitHubClient:
    def __init__(self, repository: str, token: str) -> None:
        self.repository = repository
        self.base_url = f"https://api.github.com/repos/{repository}"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def get_pull_request_files(self, pr_number: int, max_files: int) -> list[PullRequestFile]:
        response = self.session.get(f"{self.base_url}/pulls/{pr_number}/files", timeout=30)
        response.raise_for_status()
        files = []
        for item in response.json()[:max_files]:
            files.append(
                PullRequestFile(
                    filename=item["filename"],
                    status=item["status"],
                    patch=item.get("patch", ""),
                )
            )
        return files

    def list_issue_comments(self, issue_number: int) -> list[dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/issues/{issue_number}/comments", timeout=30)
        response.raise_for_status()
        return response.json()

    def upsert_issue_comment(self, issue_number: int, marker: str, body: str) -> None:
        existing = None
        for comment in self.list_issue_comments(issue_number):
            if marker in comment.get("body", ""):
                existing = comment
                break

        if existing:
            response = self.session.patch(
                existing["url"],
                json={"body": body},
                timeout=30,
            )
        else:
            response = self.session.post(
                f"{self.base_url}/issues/{issue_number}/comments",
                json={"body": body},
                timeout=30,
            )
        response.raise_for_status()

