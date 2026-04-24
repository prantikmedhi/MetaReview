from __future__ import annotations

import unittest

from metareview.metadata import OpenMetadataClient


class OpenMetadataClientTests(unittest.TestCase):
    def test_accepts_openmetadata_root_url(self) -> None:
        client = OpenMetadataClient("https://sandbox.open-metadata.org", "token")

        self.assertEqual(client.base_url, "https://sandbox.open-metadata.org/api")

    def test_accepts_openmetadata_api_url(self) -> None:
        client = OpenMetadataClient("https://sandbox.open-metadata.org/api", "token")

        self.assertEqual(client.base_url, "https://sandbox.open-metadata.org/api")


if __name__ == "__main__":
    unittest.main()
