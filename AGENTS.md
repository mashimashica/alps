# AGENTS.md

[Japanese translation](docs/ja/AGENTS.md)

## ALPS

This repository includes Skills that conform to the ALPS (Agent Lifecycle Process Skills) specification.

ALPS applies the Process Framework—which frames work around its Purpose and intended Outcomes—to Agent Skills and establishes common rules for describing the content of each Skill as a Process Description. An Activity is a cohesive set of Tasks that contribute to Outcomes, and a Process transforms Inputs into Outputs through its Activities.

ALPS treats Skill definition, application, and management as a single lifecycle. The ALPS Reference Model represents that lifecycle through three Processes and the relationships among them. These are not fixed phases; select and combine them as needed.

### Using ALPS

Keep the core policy in this section aligned with the canonical consumer-repository template in [README.md](README.md#add-repository-guidance). Repository-specific workflow rules belong in the separate section below.

- For each substantive request, use the ALPS Reference Model to select the applicable reference Skills from `define-alps`, `apply-alps`, and `manage-alps`.
- Identify other ALPS-conformant Skills by the `ALPS-conformant.` marker at the end of `description`, then assess their fit from the discovery description.
- Read each selected Skill's complete `SKILL.md` before applying it.
- Use `apply-alps` for existing Skills, `define-alps` for an unmet need or Skill redefinition, and `manage-alps` for adoption, Tailoring, assessment, change, or retirement.
- When combining Skills, make every Output/Input handoff explicit.

## Repository Workflow

- Keep the repository root on `main` by default. Perform development work in `.worktrees/<branch-name>` on a `<type>/<topic>` branch unless the user explicitly directs otherwise.
- Choose `<type>` to describe the nature of the change, never the author, Agent, or tool performing it. Prefer a conventional type such as `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, or `chore`, and write `<topic>` in concise kebab-case.
- Inspect repository state before editing and preserve unrelated or user changes.
- Keep one source of truth for each information item and use relative links from consumers.
- Assess the paired English or Japanese asset whenever one language variant changes.
- Do not commit, push, publish, open a pull request, or make another external change unless the user requests it.
- Follow the selected Skills' validation requirements. At minimum, run `git diff --check`, verify changed relative links, and inspect the final task-owned diff; report any required check not run and why.
