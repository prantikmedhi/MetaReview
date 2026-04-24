from __future__ import annotations

import unittest

from metareview.metadata import OpenMetadataClient


class FakeOpenMetadataClient(OpenMetadataClient):
    def __init__(self) -> None:
        super().__init__("https://sandbox.open-metadata.org", "token")
        self.paths: list[str] = []

    def _get(self, path, params=None):  # type: ignore[no-untyped-def]
        self.paths.append(path)
        if path.startswith("/api/v1/tables/name/"):
            return {
                "id": "table-id",
                "name": "customers",
                "fullyQualifiedName": "acme_nexus_raw_data.acme_raw.crm.customers",
                "columns": [{"name": "email", "tags": [{"tagFQN": "PII.Sensitive"}]}],
            }
        if path == "/api/v1/lineage/table/table-id":
            return {
                "downstreamEdges": [
                    {"toEntity": {"fullyQualifiedName": "dashboard.customer_health"}}
                ]
            }
        raise AssertionError(f"unexpected path: {path}")


class OpenMetadataClientTests(unittest.TestCase):
    def test_accepts_openmetadata_root_url(self) -> None:
        client = OpenMetadataClient("https://sandbox.open-metadata.org", "token")

        self.assertEqual(client.base_url, "https://sandbox.open-metadata.org/api")

    def test_accepts_openmetadata_api_url(self) -> None:
        client = OpenMetadataClient("https://sandbox.open-metadata.org/api", "token")

        self.assertEqual(client.base_url, "https://sandbox.open-metadata.org/api")

    def test_full_table_name_uses_direct_lookup_before_search(self) -> None:
        client = FakeOpenMetadataClient()

        table = client.lookup_table("acme_nexus_raw_data.acme_raw.crm.customers", 2)

        self.assertIsNotNone(table)
        self.assertEqual(table.fully_qualified_name, "acme_nexus_raw_data.acme_raw.crm.customers")
        self.assertEqual(table.pii_columns, ["email"])
        self.assertEqual(table.downstream_assets, ["dashboard.customer_health"])
        self.assertEqual(
            client.paths[0],
            "/api/v1/tables/name/acme_nexus_raw_data.acme_raw.crm.customers",
        )

    def test_accepts_string_tag_values_from_openmetadata(self) -> None:
        client = OpenMetadataClient("https://sandbox.open-metadata.org", "token")

        self.assertEqual(client._extract_tag_names(["PII.Sensitive"]), ["PII.Sensitive"])

    def test_accepts_string_column_values_from_openmetadata(self) -> None:
        client = OpenMetadataClient("https://sandbox.open-metadata.org", "token")

        column_tags, pii_columns, deprecated_columns = client._extract_column_tags(["email"])

        self.assertEqual(column_tags, {"email": []})
        self.assertEqual(pii_columns, [])
        self.assertEqual(deprecated_columns, [])


if __name__ == "__main__":
    unittest.main()
