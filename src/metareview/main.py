from __future__ import annotations

import json
import sys

from metareview.config import Settings
from metareview.github_client import GitHubClient
from metareview.metadata import OpenMetadataClient, TableMetadata
from metareview.parsing import parse_pr_files
from metareview.review import build_fallback_review, build_prompt, build_risk_summary, call_gemini, wrap_comment


def main() -> int:
    settings = Settings.from_env()

    github = GitHubClient(settings.github_repository, settings.github_token)
    om = OpenMetadataClient(
        settings.openmetadata_url,
        settings.openmetadata_jwt_token,
        settings.openmetadata_verify_ssl,
    )

    pr_files = github.get_pull_request_files(settings.pr_number, settings.metareview_max_files)
    parsed = parse_pr_files(pr_files)

    metadata_tables: list[TableMetadata] = []
    for table_name in parsed.tables:
        try:
            table = om.lookup_table(table_name, settings.openmetadata_max_downstream_depth)
        except Exception as exc:
            print(f"OpenMetadata lookup failed for {table_name}: {exc}", file=sys.stderr)
            continue
        if table:
            metadata_tables.append(table)

    risk = build_risk_summary(parsed, metadata_tables)
    prompt = build_prompt(parsed, metadata_tables, risk)

    try:
        review_body = call_gemini(settings.gemini_api_key, settings.gemini_model, prompt)
    except Exception as exc:
        print(f"Gemini generation failed: {exc}", file=sys.stderr)
        review_body = build_fallback_review(parsed, risk)

    comment = wrap_comment(review_body, risk)
    github.upsert_issue_comment(settings.pr_number, "<!-- metareview-comment -->", comment)

    print(
        json.dumps(
            {
                "pr_number": settings.pr_number,
                "touched_files": parsed.touched_files,
                "tables": parsed.tables,
                "columns": parsed.columns,
                "risk_level": risk.level,
                "risk_score": risk.score,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
