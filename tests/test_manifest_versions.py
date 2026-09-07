"""Keep native Plugin manifests aligned with the repository release version."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ManifestVersionTests(unittest.TestCase):
    def test_versions_match_release_version(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for path in (
            "plugin.json",
            ".claude-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            ".codex-plugin/plugin.json",
        ):
            with self.subTest(manifest=path):
                manifest = json.loads((ROOT / path).read_text(encoding="utf-8"))
                self.assertEqual(manifest["version"], version)


if __name__ == "__main__":
    unittest.main()
