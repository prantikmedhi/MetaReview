from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    github_token: str
    github_repository: str
    pr_number: int
    gemini_api_key: str
    gemini_model: str
    openmetadata_url: str
    openmetadata_jwt_token: str
    openmetadata_verify_ssl: bool
    openmetadata_max_downstream_depth: int
    metareview_max_files: int

    @classmethod
    def from_env(cls) -> "Settings":
        required = {
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
            "GITHUB_REPOSITORY": os.getenv("GITHUB_REPOSITORY"),
            "PR_NUMBER": os.getenv("PR_NUMBER"),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
            "OPENMETADATA_URL": os.getenv("OPENMETADATA_URL"),
            "OPENMETADATA_JWT_TOKEN": os.getenv("OPENMETADATA_JWT_TOKEN"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            github_token=required["GITHUB_TOKEN"] or "",
            github_repository=required["GITHUB_REPOSITORY"] or "",
            pr_number=int(required["PR_NUMBER"] or "0"),
            gemini_api_key=required["GEMINI_API_KEY"] or "",
            gemini_model=os.getenv("METAREVIEW_MODEL", "gemini-1.5-flash"),
            openmetadata_url=(required["OPENMETADATA_URL"] or "").rstrip("/"),
            openmetadata_jwt_token=required["OPENMETADATA_JWT_TOKEN"] or "",
            openmetadata_verify_ssl=_bool_env("OPENMETADATA_VERIFY_SSL", True),
            openmetadata_max_downstream_depth=int(os.getenv("OPENMETADATA_MAX_DOWNSTREAM_DEPTH", "2")),
            metareview_max_files=int(os.getenv("METAREVIEW_MAX_FILES", "25")),
        )

