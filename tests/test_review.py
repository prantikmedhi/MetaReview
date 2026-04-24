from __future__ import annotations

import unittest

from metareview.metadata import TableMetadata
from metareview.parsing import ParsedChanges
from metareview.review import build_fallback_review, build_risk_summary, wrap_comment


class ReviewTests(unittest.TestCase):
    def test_risk_summary_flags_pii_deprecated_and_downstream(self) -> None:
        parsed = ParsedChanges(
            sql_snippets=[
                "select email, legacy_status from acme_nexus_raw_data.acme_raw.crm.customers"
            ],
            tables=["acme_nexus_raw_data.acme_raw.crm.customers"],
            columns=[],
            touched_files=["demo/metareview_demo.sql"],
        )
        table = TableMetadata(
            name="customers",
            fully_qualified_name="acme_nexus_raw_data.acme_raw.crm.customers",
            pii_columns=["email"],
            deprecated_columns=["legacy_status"],
            downstream_assets=["dashboard.customer_health"],
        )

        risk = build_risk_summary(parsed, [table])

        self.assertEqual(risk.level, "MEDIUM")
        self.assertEqual(risk.score, 5.6)
        self.assertEqual(risk.pii_hits, ["customers.email"])
        self.assertEqual(risk.deprecated_hits, ["customers.legacy_status"])
        self.assertEqual(risk.downstream_assets, ["dashboard.customer_health"])

    def test_fallback_review_and_wrapper_include_operational_context(self) -> None:
        parsed = ParsedChanges(
            sql_snippets=["select * from crm.customers"],
            tables=["crm.customers"],
            columns=[],
            touched_files=["models/customers.sql"],
        )
        risk = build_risk_summary(parsed, [])

        review = build_fallback_review(parsed, risk)
        comment = wrap_comment(review, risk)

        self.assertIn("<!-- metareview-comment -->", comment)
        self.assertIn("**Impact Score:** `LOW` (1.0/10)", comment)
        self.assertIn("models/customers.sql", comment)
        self.assertIn("crm.customers", comment)

    def test_risk_summary_does_not_flag_unreferenced_table_column_name(self) -> None:
        parsed = ParsedChanges(
            sql_snippets=["select email from crm.orders"],
            tables=["crm.orders"],
            columns=[],
            touched_files=["models/orders.sql"],
        )
        table = TableMetadata(
            name="customers",
            fully_qualified_name="crm.customers",
            pii_columns=["email"],
            downstream_assets=["dashboard.customer_health"],
        )

        risk = build_risk_summary(parsed, [table])

        self.assertEqual(risk.level, "LOW")
        self.assertEqual(risk.score, 1.0)
        self.assertEqual(risk.pii_hits, [])
        self.assertEqual(risk.downstream_assets, [])

    def test_risk_summary_flags_sensitive_sql_column_names_without_metadata(self) -> None:
        parsed = ParsedChanges(
            sql_snippets=["select email, phone_number from crm.customers"],
            tables=["crm.customers"],
            columns=[],
            touched_files=["models/customers.sql"],
        )

        risk = build_risk_summary(parsed, [])

        self.assertEqual(risk.level, "MEDIUM")
        self.assertEqual(risk.score, 6.0)
        self.assertEqual(risk.pii_hits, ["email", "phone_number"])

    def test_risk_summary_flags_sensitive_sql_column_names_when_metadata_lacks_tags(self) -> None:
        parsed = ParsedChanges(
            sql_snippets=["select email, phone_number from crm.customers"],
            tables=["crm.customers"],
            columns=[],
            touched_files=["models/customers.sql"],
        )
        table = TableMetadata(
            name="customers",
            fully_qualified_name="crm.customers",
        )

        risk = build_risk_summary(parsed, [table])

        self.assertEqual(risk.level, "MEDIUM")
        self.assertEqual(risk.score, 6.0)
        self.assertEqual(risk.pii_hits, ["email", "phone_number"])


if __name__ == "__main__":
    unittest.main()
