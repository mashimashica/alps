# pstack in ALPS form

[Japanese translation](locales/ja/README.md)

This directory tree is an unofficial conversion of the pstack Plugin into ALPS form. It is reference material for the two ALPS design Skills. It is not affiliated with or endorsed by pstack's author.

## Source

| Item | Value |
| --- | --- |
| Plugin | pstack 0.15.44 |
| Repository | `https://github.com/cursor/plugins`, path `pstack/` |
| Commit | `e58dd043600587dbaf58ba315e7f2b38373eeb43` |
| License | MIT, Copyright (c) 2026 Lauren Tan. See [LICENSE](../../LICENSE). |

The first commits that add this tree to the ALPS repository hold the upstream files unchanged, so the conversion can be read as a diff against the upstream bytes.

## Status

The conversion is in progress.

- Done: every Skill body, every poteto-mode playbook, and the reviewing agent definition are rewritten as Process Descriptions with a derived Purpose and derived Outcomes. Tool-use references exist for the four bundled tools. Frontmatter, scripts, data files, the worker rules, the bootstrapping agent definition, and the Claude Code adapter are unchanged from upstream.
- In progress: independent fidelity and Framework reviews of each converted file, and the fixes they call for.
- Not yet done: verification of the recorded source findings, trials on representative work, and the full guide with per-file records.

The Purposes and Outcomes are derived by the conversion. The upstream author did not write them and has not confirmed them. Until the reviews and trials are complete, do not rely on this tree as equivalent to upstream pstack.
