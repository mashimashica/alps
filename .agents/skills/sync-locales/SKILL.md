---
name: sync-locales
description: Check and synchronize semantic equivalence between the authoritative English ALPS assets and their Japanese counterparts, including omissions introduced by repository changes. Use when English or Japanese specifications, reference Processes, guidance, templates, or bindings change. Repository-development Skill; not part of the distributed ALPS Plugin.
---

# Sync Locales

Use `localization.yaml` as the locale policy. English is authoritative and Japanese is supported unless that policy changes.

## Scope

Check the applicable English/Japanese pairs, including:

- `spec/*.md` and `spec/locales/ja/*.md`;
- `skills/*/SKILL.md` and `skills/*/references/locales/ja/SKILL.md`;
- paired reference, template, and binding assets under distributed Skills when localized counterparts exist; and
- `README.md` / `docs/ja/README.md`, `AGENTS.md` / `docs/ja/AGENTS.md`, and other explicitly paired repository guidance.

Do not treat repository-development Skills under `.agents/skills/` as Plugin locale assets unless localized versions are deliberately introduced.

## Comparison method

1. Determine which side changed and identify the corresponding semantic units on the other side.
2. Compare meaning, not sentence shape. Preserve terminology and structure where they carry ALPS semantics.
3. Check that Purpose, Outcomes, Activities, Tasks, requirements, recommendations, permissions, prohibitions, Conformance boundaries, references, examples, identifiers, code literals, and status words have no material omission or addition.
4. Preserve normative force. In particular, do not weaken or strengthen `must`, `should`, `may`, or their Japanese equivalents.
5. Keep canonical identifiers, paths, metadata keys, code, and reference forms unchanged unless the source itself changed.
6. Treat a Japanese statement with no supported English source, or an English statement omitted from Japanese, as a semantic mismatch unless it is clearly locale-specific presentation.
7. When synchronization is requested, update the supported locale to match the authoritative English meaning. Do not silently rewrite the English source from the Japanese translation.
8. Recheck the resulting pair and inspect the final diff for unrelated translation drift.

## Result

Report each mismatch with the paired files, the affected semantic unit, and the required correction. Distinguish semantic differences from harmless wording differences.

If the pair is semantically equivalent, state that explicitly. Report any pair that could not be checked rather than assuming equivalence.
