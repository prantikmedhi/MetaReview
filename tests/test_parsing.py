from __future__ import annotations

import unittest

from metareview.github_client import PullRequestFile
from metareview.parsing import parse_pr_files


class ParsingTests(unittest.TestCase):
    def test_extracts_fully_qualified_table_from_sql_patch(self) -> None:
        parsed = parse_pr_files(
            [
                PullRequestFile(
                    filename="models/customer_health.sql",
                    status="modified",
                    patch="""@@ -0,0 +1,5 @@
+select
+  customer_id,
+  email
+from acme_nexus_raw_data.acme_raw.crm.customers;
""",
                )
            ]
        )

        self.assertEqual(parsed.tables, ["acme_nexus_raw_data.acme_raw.crm.customers"])
        self.assertEqual(parsed.touched_files, ["models/customer_health.sql"])
        self.assertIn("email", parsed.sql_snippets[0])

    def test_normalizes_quoted_table_identifier(self) -> None:
        parsed = parse_pr_files(
            [
                PullRequestFile(
                    filename="warehouse/customers.sql",
                    status="modified",
                    patch="""@@ -0,0 +1,2 @@
+select c.email
+from `acme_nexus_raw_data`.`acme_raw`.`crm`.`customers` c;
""",
                )
            ]
        )

        self.assertEqual(parsed.tables, ["acme_nexus_raw_data.acme_raw.crm.customers"])
        self.assertEqual(parsed.columns, ["c.email"])

    def test_does_not_treat_fully_qualified_table_as_column(self) -> None:
        parsed = parse_pr_files(
            [
                PullRequestFile(
                    filename="warehouse/customers.sql",
                    status="modified",
                    patch="""@@ -0,0 +1,2 @@
+select email
+from acme_nexus_raw_data.acme_raw.crm.customers;
""",
                )
            ]
        )

        self.assertEqual(parsed.tables, ["acme_nexus_raw_data.acme_raw.crm.customers"])
        self.assertEqual(parsed.columns, [])

    def test_extracts_dbt_ref_and_source_macros(self) -> None:
        parsed = parse_pr_files(
            [
                PullRequestFile(
                    filename="models/customer_orders.sql",
                    status="modified",
                    patch="""@@ -0,0 +1,3 @@
+select *
+from {{ ref("orders") }} o
+join {{ source('raw', 'customers') }} c on c.customer_id = o.customer_id
""",
                )
            ]
        )

        self.assertEqual(parsed.tables, ["orders", "raw.customers"])
        self.assertEqual(parsed.columns, ["c.customer_id", "o.customer_id"])

    def test_does_not_treat_column_alias_as_table(self) -> None:
        parsed = parse_pr_files(
            [
                PullRequestFile(
                    filename="model.sql",
                    status="modified",
                    patch="""@@ -0,0 +1,2 @@
+select c.email
+from crm.customers c;
""",
                )
            ]
        )

        self.assertEqual(parsed.tables, ["crm.customers"])
        self.assertNotIn("c", parsed.tables)

    def test_ignores_non_sql_patch(self) -> None:
        parsed = parse_pr_files(
            [
                PullRequestFile(
                    filename="README.md",
                    status="modified",
                    patch="""@@ -1 +1 @@
+This is prose without query text.
""",
                )
            ]
        )

        self.assertEqual(parsed.tables, [])
        self.assertEqual(parsed.touched_files, [])


if __name__ == "__main__":
    unittest.main()
