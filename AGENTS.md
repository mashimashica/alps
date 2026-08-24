# AGENTS.md

[Japanese translation](docs/ja/AGENTS.md)

## ALPS

This repository contains Agent Skills that represent Process Framework constructs under ALPS.

ALPS starts from the ordinary Process case: an Agent Skill represents a Process through an authoritative Process Description. ALPS also permits Agent Skills to represent a Process Model, Process Reference Model, or Process View. These non-Process representations are identified by `metadata.alps.kind`; activating them loads selection or composition context and does not itself invoke a Process.

The ALPS Reference Model is represented by `alps-reference-model` and defines three reference Processes: Define ALPS, Apply ALPS, and Manage ALPS. They are not fixed phases and may be selected, combined, iterated, or revisited according to the application situation.

### Using ALPS

- Activate `alps-reference-model` when the ALPS Reference Model is needed to select, relate, assess, or improve the reference Processes.
- Treat an Agent Skill as a Process representation by default. If `metadata.alps.kind` declares `process-model`, `process-reference-model`, or `process-view`, load the representation without treating activation as Process Invocation.
- Read the complete `SKILL.md` for each selected representation before relying on it.
- Use `define-alps` to define or verify an ALPS representation, including a Process Description, Process Model, Process Reference Model, or Process View.
- Use `apply-alps` to activate applicable Models or Views, resolve referenced Processes, invoke only Process representations, and manage required handoffs.
- Use `manage-alps` for adoption, status, controlled change, Tailoring, formal adoption, assessment, improvement, or retirement of managed representations.
- Resolve canonical Skill references before relying on the referenced Process. Do not substitute a repository-relative path for representation identity.
- For a Process View, preserve provenance and Traceability for referenced source elements and keep View-specific or modified Activities and Tasks distinct from changes to Source Processes.

## Repository Workflow

- Keep the repository root on `main` by default. Perform development work in `.worktrees/<branch-name>` on a `<type>/<topic>` branch unless the user explicitly directs otherwise.
- Choose `<type>` to describe the nature of the change, never the author, Agent, or tool performing it. Prefer a conventional type such as `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, or `chore`, and write `<topic>` in concise kebab-case.
- Inspect repository state before editing and preserve unrelated or user changes.
- Keep one authoritative source for each information item. Where the Process Framework requires the same semantic center in more than one representation, verify equality mechanically rather than establishing precedence between divergent copies.
- Assess the paired English or Japanese asset whenever one language variant changes.
- Do not commit, push, publish, open a pull request, or make another external change unless the user requests it.
- Follow the selected representations' validation requirements. At minimum, run `git diff --check`, verify changed relative links, run applicable ALPS asset checks, and inspect the final task-owned diff; report any required check not run and why.
