"""Keep Japanese translation manifests complete and tied to reviewed sources."""

import hashlib
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIPPED_DIRECTORIES = {".git", ".claude", "node_modules"}


def locale_directories():
    """Yield every `locales/ja` directory without following symlinks."""
    for directory, subdirectories, _ in os.walk(ROOT, followlinks=False):
        subdirectories[:] = [
            entry for entry in subdirectories if entry not in SKIPPED_DIRECTORIES
        ]
        path = Path(directory)
        if path.name == "ja" and path.parent.name == "locales":
            yield path


def parse_manifest(path: Path) -> dict:
    """Parse the manifest's fixed YAML subset.

    Top-level scalars, plus a `sources` mapping whose entries map a translated
    path to `source` and `reviewed_source_sha256` scalars.
    """
    manifest: dict = {}
    current = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, separator, value = raw.strip().partition(":")
        if not separator:
            raise ValueError(f"{path}:{number}: expected 'key: value'")
        value = value.strip().strip('"')
        if indent == 0:
            if key == "sources" and not value:
                manifest["sources"] = {}
            else:
                manifest[key] = value
            current = None
        elif indent == 2 and "sources" in manifest and not value:
            current = manifest["sources"].setdefault(key, {})
        elif indent == 4 and current is not None:
            current[key] = value
        else:
            raise ValueError(f"{path}:{number}: unsupported structure")
    return manifest


class LocaleManifestTests(unittest.TestCase):
    def test_manifests_register_translations_with_current_source_hashes(self) -> None:
        directories = sorted(locale_directories())
        self.assertTrue(directories)
        for directory in directories:
            relative_directory = directory.relative_to(ROOT).as_posix()
            manifest_path = directory / "manifest.yaml"
            with self.subTest(locale_directory=relative_directory):
                self.assertTrue(manifest_path.is_file(), "missing manifest.yaml")
                manifest = parse_manifest(manifest_path)
                self.assertEqual(manifest.get("locale"), "ja")
                self.assertEqual(manifest.get("source_locale"), "en")
                self.assertTrue(manifest.get("status"))
                sources = manifest.get("sources", {})

                translations = {
                    path.relative_to(directory).as_posix()
                    for path in directory.rglob("*.md")
                }
                self.assertEqual(
                    translations - set(sources),
                    set(),
                    "Japanese files missing from manifest",
                )

            for translated, entry in sorted(sources.items()):
                with self.subTest(manifest=relative_directory, translation=translated):
                    self.assertTrue((directory / translated).is_file())
                    source = directory / entry.get("source", "")
                    self.assertTrue(
                        entry.get("source") and source.is_file(),
                        "source file does not exist",
                    )
                    digest = hashlib.sha256(source.read_bytes()).hexdigest()
                    self.assertEqual(
                        entry.get("reviewed_source_sha256"),
                        digest,
                        f"{entry['source']} changed since review; review the "
                        "translation and update reviewed_source_sha256",
                    )


if __name__ == "__main__":
    unittest.main()
