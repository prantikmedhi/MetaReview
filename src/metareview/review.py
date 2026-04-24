from __future__ import annotations

import json
import re
from dataclasses import dataclass

import requests

from metareview.metadata import TableMetadata
from metareview.parsing import ParsedChanges

COMMENT_MARKER = "<!-- metareview-comment -->"


@dataclass
class RiskSummary:
    score: float
    level: str
    pii_hits: list[str]
    deprecated_hits: list[str]
    downstream_assets: list[str]


def build_risk_summary(parsed: ParsedChanges, tables: list[TableMetadata]) -> RiskSummary:
    pii_hits: list[str] = []
    deprecated_hits: list[str] = []
    downstream_assets: set[str] = set()
    sql_blob = "\n".join(parsed.sql_snippets)

    def table_referenced(table: TableMetadata) -> bool:
        if not parsed.tables:
            return True
        names = {table.name, table.fully_qualified_name}
        return any(parsed_table in names or parsed_table.endswith(f".{table.name}") for parsed_table in parsed.tables)

    def column_referenced(table_name: str, column_name: str) -> bool:
        fully_qualified = f"{table_name}.{column_name}"
        return fully_qualified in parsed.columns or bool(
            re.search(rf"\b{re.escape(column_name)}\b", sql_blob, flags=re.IGNORECASE)
        )

    for table in tables:
        if not table_referenced(table):
            continue

        downstream_assets.update(table.downstream_assets)

        for column in table.pii_columns:
            full_name = f"{table.name}.{column}"
            if column_referenced(table.name, column):
                pii_hits.append(full_name)

        for column in table.deprecated_columns:
            full_name = f"{table.name}.{column}"
            if column_referenced(table.name, column):
                deprecated_hits.append(full_name)

    score = 1.0
    score += min(len(pii_hits) * 2.5, 5.0)
    score += min(len(deprecated_hits) * 1.5, 3.0)
    score += min(len(downstream_assets) * 0.6, 3.0)

    if score >= 7.0:
        level = "HIGH"
    elif score >= 4.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    return RiskSummary(
        score=round(min(score, 10.0), 1),
        level=level,
        pii_hits=sorted(set(pii_hits)),
        deprecated_hits=sorted(set(deprecated_hits)),
        downstream_assets=sorted(downstream_assets),
    )


def build_prompt(parsed: ParsedChanges, tables: list[TableMetadata], risk: RiskSummary) -> str:
    metadata_payload = {
        "touched_files": parsed.touched_files,
        "tables": parsed.tables,
        "columns": parsed.columns,
        "risk": {
            "score": risk.score,
            "level": risk.level,
            "pii_hits": risk.pii_hits,
            "deprecated_hits": risk.deprecated_hits,
            "downstream_assets": risk.downstream_assets,
        },
        "openmetadata": [
            {
                "name": table.name,
                "fully_qualified_name": table.fully_qualified_name,
                "description": table.description,
                "tags": table.tags,
                "column_tags": table.columns,
                "pii_columns": table.pii_columns,
                "deprecated_columns": table.deprecated_columns,
                "downstream_assets": table.downstream_assets,
            }
            for table in tables
        ],
        "sql_snippets": parsed.sql_snippets[:4],
    }
    return (
        "You are MetaReview, a senior data platform reviewer. "
        "Write a concise, professional pull request review in markdown. "
        "Include sections titled Summary, Risks, Impact, and Recommended Action. "
        "Use plain engineering language, do not invent facts, and do not mention missing data unless important. "
        "Start with one-line verdict. "
        "Context:\n"
        + json.dumps(metadata_payload, indent=2)
    )


def call_gemini(api_key: str, model: str, prompt: str) -> str:
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                    ]
                }
            ]
        },
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini returned no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise ValueError("Gemini returned empty text")
    return text


def build_fallback_review(parsed: ParsedChanges, risk: RiskSummary) -> str:
    summary = f"MetaReview assessed this PR as **{risk.level}** risk with score **{risk.score}/10**."
    risks = []
    if risk.pii_hits:
        risks.append(f"- PII-sensitive fields detected: {', '.join(risk.pii_hits)}")
    if risk.deprecated_hits:
        risks.append(f"- Deprecated fields referenced: {', '.join(risk.deprecated_hits)}")
    if risk.downstream_assets:
        risks.append(f"- Downstream assets potentially affected: {', '.join(risk.downstream_assets[:6])}")
    if not risks:
        risks.append("- No critical metadata risks detected from available context.")

    action = "- Validate schema compatibility before merge.\n- Confirm downstream owners are aware if lineage impact is expected."

    return "\n".join(
        [
            "## Summary",
            summary,
            "",
            "## Risks",
            *risks,
            "",
            "## Impact",
            f"- SQL-bearing files analyzed: {', '.join(parsed.touched_files) if parsed.touched_files else 'None'}",
            f"- Referenced tables: {', '.join(parsed.tables) if parsed.tables else 'None detected'}",
            "",
            "## Recommended Action",
            action,
        ]
    )


def wrap_comment(review_body: str, risk: RiskSummary) -> str:
    banner = (
        f"{COMMENT_MARKER}\n"
        f"# MetaReview Bot\n\n"
        f"**Impact Score:** `{risk.level}` ({risk.score}/10)\n\n"
    )
    return banner + review_body.strip() + "\n"
