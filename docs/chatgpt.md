# Using ALPS in ChatGPT web and mobile

ChatGPT can install uploaded Agent Skills, but personal Skills are managed separately for desktop and web/mobile. ALPS therefore provides a standalone export path for the three reference Skills without changing the repository's authoritative Skill Packages.

> Availability depends on the ChatGPT plan and workspace settings. See the current OpenAI Skills documentation before relying on this workflow for a managed workspace.

## Export the Skills

From the repository root, run:

```console
python3 scripts/export_agent_skills.py --target chatgpt
```

This writes three self-contained Skill directories under `dist/chatgpt/`:

```text
dist/chatgpt/
├── define-alps/
├── apply-alps/
└── manage-alps/
```

Each exported directory contains its root `SKILL.md`, its existing bundled resources, and a package-local copy of the shared ALPS normative specification under `references/alps/spec/`. Links that normally point to the repository-level `.alps/spec` tree are rewritten only in the generated copy so that they remain resolvable after standalone upload.

To export only one Skill, repeat `--skill` as needed:

```console
python3 scripts/export_agent_skills.py --target chatgpt --skill apply-alps
```

Generated files under `dist/` are disposable build outputs and are not source-of-truth assets.

## Install for web/mobile

1. In ChatGPT on the web, open **Plugins** and then **Skills**.
2. Choose **Create** and **Upload from your computer**.
3. Upload each exported Agent Skill you want to use.
4. Install the uploaded Skill for the web/mobile surface when prompted.
5. Open ChatGPT on mobile and invoke the Skill by name when you want to force a particular ALPS Process, for example: `Use apply-alps to ...`.

OpenAI currently documents desktop and web/mobile personal Skills as separate installations, so installing a Skill only for desktop does not make it available on mobile automatically.

## Why export instead of copying `skills/`

The authoritative ALPS Skill Descriptions intentionally share repository-level normative assets in `.alps/spec`. A raw copy of `skills/apply-alps`, `skills/define-alps`, or `skills/manage-alps` therefore leaves those repository-relative references unresolved outside this repository. The exporter preserves the maintained source layout while producing a self-contained transport copy for upload-oriented clients.

## Validation

Run the exporter tests with:

```console
python3 -m unittest tests/test_export_agent_skills.py
```

The exporter also verifies every generated Skill and fails if a root `SKILL.md`, the bundled specification, or repository-escaping `.alps/spec` links are missing or unresolved.
