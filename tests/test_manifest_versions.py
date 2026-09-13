"""Keep native Plugin manifests aligned with the repository release version."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    "plugin.json",
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".codex-plugin/plugin.json",
)
MARKETPLACE = ".claude-plugin/marketplace.json"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def marketplace_entry() -> dict:
    root_name = load("plugin.json")["name"]
    entries = [
        entry for entry in load(MARKETPLACE)["plugins"] if entry.get("name") == root_name
    ]
    if len(entries) != 1:
        raise AssertionError(f"{MARKETPLACE} must list {root_name} exactly once")
    return entries[0]


class ManifestVersionTests(unittest.TestCase):
    def test_versions_match_release_version(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for path in MANIFESTS:
            with self.subTest(manifest=path):
                self.assertEqual(load(path)["version"], version)
        with self.subTest(manifest=MARKETPLACE):
            # plugin.json governs the version; a marketplace pin would duplicate it.
            self.assertNotIn("version", marketplace_entry())

    def test_names_and_descriptions_match(self) -> None:
        root = load("plugin.json")
        for key in ("name", "description"):
            for path in MANIFESTS[1:]:
                manifest = load(path)
                if key in manifest:
                    with self.subTest(manifest=path, key=key):
                        self.assertEqual(manifest[key], root[key])
            entry = marketplace_entry()
            if key in entry:
                with self.subTest(manifest=MARKETPLACE, key=key):
                    self.assertEqual(entry[key], root[key])
        with self.subTest(manifest=MARKETPLACE, key="metadata.description"):
            self.assertEqual(load(MARKETPLACE)["metadata"]["description"], root["description"])


if __name__ == "__main__":
    unittest.main()
