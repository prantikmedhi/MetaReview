from __future__ import annotations

import re
from dataclasses import dataclass

from metareview.github_client import PullRequestFile

SQL_FILE_EXTENSIONS = (".sql", ".ddl", ".dml")
TEXT_SQL_EXTENSIONS = (".py", ".yml", ".yaml", ".json", ".txt", ".md")
IDENTIFIER_PART = r'(?:[a-zA-Z_][\w$]*|`[^`]+`|"[^"]+")'
TABLE_PATTERN = re.compile(
    rf"\b(?:from|join|update|into|table)\s+({IDENTIFIER_PART}(?:\.{IDENTIFIER_PART})*)",
    flags=re.IGNORECASE,
)
COLUMN_PATTERN = re.compile(r"(?<![.\w])([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)(?![.\w])")
DBT_REF_PATTERN = re.compile(r"\{\{\s*ref\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}")
DBT_SOURCE_PATTERN = re.compile(
    r"\{\{\s*source\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}"
)


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


def _normalize_identifier(identifier: str) -> str:
    parts = []
    for part in identifier.split("."):
        parts.append(part.strip().strip("`\""))
    return ".".join(part for part in parts if part)


def _overlaps(span: tuple[int, int], blocked_spans: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < blocked_end and end > blocked_start for blocked_start, blocked_end in blocked_spans)


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

        for match in DBT_REF_PATTERN.findall(sql_text):
            tables.add(match)
        for source_name, table_name in DBT_SOURCE_PATTERN.findall(sql_text):
            tables.add(f"{source_name}.{table_name}")

        table_spans: list[tuple[int, int]] = []
        for match in TABLE_PATTERN.finditer(sql_text):
            identifier = match.group(1)
            normalized = _normalize_identifier(identifier)
            if normalized:
                tables.add(normalized)
            table_spans.append(match.span(1))

        for match in COLUMN_PATTERN.finditer(sql_text):
            if _overlaps(match.span(), table_spans):
                continue
            table_name, column_name = match.groups()
            columns.add(f"{table_name}.{column_name}")

    return ParsedChanges(
        sql_snippets=snippets,
        tables=sorted(tables),
        columns=sorted(columns),
        touched_files=touched_files,
    )
