from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

import requests


def _normalize_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if not normalized:
        raise ValueError("OpenMetadata base URL cannot be empty")
    if normalized.endswith("/api"):
        return normalized
    return f"{normalized}/api"


@dataclass
class TableMetadata:
    name: str
    fully_qualified_name: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    columns: dict[str, list[str]] = field(default_factory=dict)
    downstream_assets: list[str] = field(default_factory=list)
    deprecated_columns: list[str] = field(default_factory=list)
    pii_columns: list[str] = field(default_factory=list)


class OpenMetadataClient:
    def __init__(self, base_url: str, jwt_token: str, verify_ssl: bool = True) -> None:
        self.base_url = _normalize_base_url(base_url)
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized_path = path.lstrip("/")
        if normalized_path.startswith("api/"):
            normalized_path = normalized_path[4:]
        response = self.session.get(
            f"{self.base_url}/{normalized_path}",
            params=params,
            timeout=30,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def _extract_tag_names(self, values: list[dict[str, Any]]) -> list[str]:
        tags: list[str] = []
        for value in values:
            tag_fqn = value.get("tagFQN")
            if tag_fqn:
                tags.append(tag_fqn)
        return tags

    def _extract_column_tags(self, columns: list[dict[str, Any]]) -> tuple[dict[str, list[str]], list[str], list[str]]:
        column_tags: dict[str, list[str]] = {}
        pii_columns: list[str] = []
        deprecated_columns: list[str] = []

        for column in columns:
            name = column.get("name", "")
            tags = self._extract_tag_names(column.get("tags", []))
            column_tags[name] = tags

            description = (column.get("description") or "").lower()
            tag_blob = " ".join(tags).lower()
            if any(word in tag_blob for word in ("pii", "sensitive", "email", "ssn")):
                pii_columns.append(name)
            if "deprecated" in description or "deprecated" in tag_blob:
                deprecated_columns.append(name)

        return column_tags, pii_columns, deprecated_columns

    def _build_table_metadata(self, entity: dict[str, Any], fqn: str, max_depth: int) -> TableMetadata:
        entity_id = entity.get("id")
        columns = entity.get("columns", [])
        column_tags, pii_columns, deprecated_columns = self._extract_column_tags(columns)
        table_tags = self._extract_tag_names(entity.get("tags", []))

        downstream_assets: list[str] = []
        if entity_id:
            lineage = self._get(
                f"/api/v1/lineage/table/{entity_id}",
                params={"upstreamDepth": 0, "downstreamDepth": max_depth},
            )
            for node in lineage.get("downstreamEdges", []):
                to_entity = node.get("toEntity", {})
                label = to_entity.get("fullyQualifiedName") or to_entity.get("name")
                if label:
                    downstream_assets.append(label)

        return TableMetadata(
            name=entity.get("name", fqn.split(".")[-1]),
            fully_qualified_name=fqn,
            description=entity.get("description") or "",
            tags=table_tags,
            columns=column_tags,
            downstream_assets=sorted(set(downstream_assets)),
            deprecated_columns=sorted(set(deprecated_columns)),
            pii_columns=sorted(set(pii_columns)),
        )

    def lookup_table(self, table_name: str, max_depth: int) -> TableMetadata | None:
        if "." in table_name:
            try:
                entity = self._get("/api/v1/tables/name/" + quote(table_name, safe=""))
                fqn = entity.get("fullyQualifiedName") or table_name
                return self._build_table_metadata(entity, fqn, max_depth)
            except requests.HTTPError as exc:
                if exc.response is None or exc.response.status_code != 404:
                    raise

        search = self._get(
            "/api/v1/search/query",
            params={"q": f'name:{table_name}', "index": "table_search_index"},
        )
        hits = search.get("hits", {}).get("hits", [])
        if not hits:
            return None

        source = hits[0].get("_source", {})
        fqn = source.get("fullyQualifiedName") or source.get("name")
        if not fqn:
            return None

        table = self._get("/api/v1/tables/name/" + quote(fqn, safe=""))
        return self._build_table_metadata(table, fqn, max_depth)
