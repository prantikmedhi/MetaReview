from __future__ import annotations

import unittest
from typing import Any

from metareview.github_client import GitHubClient


class FakeResponse:
    def __init__(self, payload: Any = None, next_url: str | None = None) -> None:
        self.payload = payload
        self.links = {"next": {"url": next_url}} if next_url else {}

    def json(self) -> Any:
        return self.payload

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, comments: list[dict[str, Any]]) -> None:
        self.headers: dict[str, str] = {}
        self.comments = comments
        self.pages: dict[str, tuple[list[dict[str, Any]], str | None]] = {}
        self.get_calls: list[tuple[str, dict[str, int] | None]] = []
        self.patch_calls: list[tuple[str, dict[str, str]]] = []
        self.post_calls: list[tuple[str, dict[str, str]]] = []

    def get(
        self, url: str, params: dict[str, int] | None = None, timeout: int = 30
    ) -> FakeResponse:
        self.get_calls.append((url, params))
        if url in self.pages:
            payload, next_url = self.pages[url]
            return FakeResponse(payload, next_url)
        return FakeResponse(self.comments)

    def patch(self, url: str, json: dict[str, str], timeout: int) -> FakeResponse:
        self.patch_calls.append((url, json))
        return FakeResponse()

    def post(self, url: str, json: dict[str, str], timeout: int) -> FakeResponse:
        self.post_calls.append((url, json))
        return FakeResponse()


class GitHubClientTests(unittest.TestCase):
    def test_upsert_updates_existing_marker_comment(self) -> None:
        client = GitHubClient("owner/repo", "token")
        session = FakeSession(
            [{"url": "https://api.github.com/comment/1", "body": "old <!-- marker -->"}]
        )
        client.session = session  # type: ignore[assignment]

        client.upsert_issue_comment(7, "<!-- marker -->", "new body")

        self.assertEqual(
            session.patch_calls,
            [("https://api.github.com/comment/1", {"body": "new body"})],
        )
        self.assertEqual(session.post_calls, [])

    def test_upsert_creates_comment_when_marker_missing(self) -> None:
        client = GitHubClient("owner/repo", "token")
        session = FakeSession([{"url": "https://api.github.com/comment/1", "body": "other"}])
        client.session = session  # type: ignore[assignment]

        client.upsert_issue_comment(7, "<!-- marker -->", "new body")

        self.assertEqual(session.patch_calls, [])
        self.assertEqual(
            session.post_calls,
            [("https://api.github.com/repos/owner/repo/issues/7/comments", {"body": "new body"})],
        )

    def test_get_pull_request_files_follows_pagination_to_max_files(self) -> None:
        client = GitHubClient("owner/repo", "token")
        session = FakeSession([])
        session.pages = {
            "https://api.github.com/repos/owner/repo/pulls/3/files": (
                [{"filename": f"file_{index}.sql", "status": "modified", "patch": "+select 1"} for index in range(100)],
                "https://api.github.com/page/2",
            ),
            "https://api.github.com/page/2": (
                [{"filename": "file_100.sql", "status": "modified", "patch": "+select 2"}],
                None,
            ),
        }
        client.session = session  # type: ignore[assignment]

        files = client.get_pull_request_files(3, 101)

        self.assertEqual(len(files), 101)
        self.assertEqual(files[-1].filename, "file_100.sql")
        self.assertEqual(
            session.get_calls[0],
            ("https://api.github.com/repos/owner/repo/pulls/3/files", {"per_page": 100}),
        )

    def test_upsert_finds_marker_on_later_comment_page(self) -> None:
        client = GitHubClient("owner/repo", "token")
        session = FakeSession([])
        session.pages = {
            "https://api.github.com/repos/owner/repo/issues/7/comments": (
                [{"url": "https://api.github.com/comment/1", "body": "other"}],
                "https://api.github.com/comments?page=2",
            ),
            "https://api.github.com/comments?page=2": (
                [{"url": "https://api.github.com/comment/2", "body": "<!-- marker -->"}],
                None,
            ),
        }
        client.session = session  # type: ignore[assignment]

        client.upsert_issue_comment(7, "<!-- marker -->", "new body")

        self.assertEqual(
            session.patch_calls,
            [("https://api.github.com/comment/2", {"body": "new body"})],
        )
        self.assertEqual(session.post_calls, [])


if __name__ == "__main__":
    unittest.main()
