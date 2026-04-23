from __future__ import annotations

import re
from dataclasses import dataclass

from metareview.github_client import PullRequestFile

SQL_FILE_EXTENSIONS = (".sql", ".ddl", ".dml")
TEXT_SQL_EXTENSIONS = (".py", ".yml", ".yaml", ".json", ".txt", ".md")
TABLE_PATTERN = re.compile(
    r"\b(?:from|join|update|into|table)\s+([a-zA-Z_][\w$.]*)",
    flags=re.IGNORECASE,
)
COLUMN_PATTERN = re.compile(r"\b([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)\b")


@dataclass
class ParsedChanges:
    sql_snippets: list[str]
    tables: list[str]
    columns: list[str]
    touched_files: list[str]


def _looks_sql_like(filename: str, patch: str) -> bool:
    lowered = filename.lower()
    if lowered.endswith(SQL_FILE_EXTENSIONS):
        return True
    if lowered.endswith(TEXT_SQL_EXTENSIONS):
        keywords = ("select ", "join ", "where ", "with ", "insert ", "update ", "from ")
        patch_lower = patch.lower()
        return any(keyword in patch_lower for keyword in keywords)
    return False


def _extract_added_lines(patch: str) -> str:
    lines: list[str] = []
    for line in patch.splitlines():
        if line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            lines.append(line[1:])
    return "\n".join(lines)


def parse_pr_files(files: list[PullRequestFile]) -> ParsedChanges:
    snippets: list[str] = []
    tables: set[str] = set()
    columns: set[str] = set()
    touched_files: list[str] = []

    for file in files:
        if not file.patch:
            continue
        if not _looks_sql_like(file.filename, file.patch):
            continue

        sql_text = _extract_added_lines(file.patch)
        if not sql_text.strip():
            continue

        snippets.append(sql_text.strip())
        touched_files.append(file.filename)

        for match in TABLE_PATTERN.findall(sql_text):
            tables.add(match.strip("`"))
        for table_name, column_name in COLUMN_PATTERN.findall(sql_text):
            tables.add(table_name)
            columns.add(f"{table_name}.{column_name}")

    return ParsedChanges(
        sql_snippets=snippets,
        tables=sorted(tables),
        columns=sorted(columns),
        touched_files=touched_files,
    )

