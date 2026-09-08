# Focused A/C staging helper

`prepare_focused.py` is assessment preparation for the user's authorized 44-trial closeout in `interim-report-2026-09-08.md`: 12 fresh A creators, 24 fresh A consumers, and the separately scheduled eight pending C consumers. It does not reopen core development or implement the original full A/B stage. Existing C assignments, recovered evidence, ledgers, cases, and helper files stay intact. The helper does not launch agents, grade work, edit product files, or write remotely.

| A creators | Existing paired C creators | Family | A consumers |
| --- | --- | --- | --- |
| focus-001–004 | control-019/020/023/024 | S03, description guidance | F-U001–008 |
| focus-005–008 | control-043/044/047/048 | S06, work-system guidance | F-U009–016 |
| focus-009–012 | control-067/068/071/072 | S10, both design responsibilities | F-U017–024 |

Each group is sol/high repetitions 1/2, then astra/high repetitions 1/2. Both consumers remain attached to their generated Skill. Pair identities and configuration are only in coordinator metadata. Creator prompts derive from the exact paired C prompt: rebind its task directory, then append only the assigned frozen ALPS support. The twelve normalized C prompts share a pinned hash. No observed business failure or grader conclusion supplies additional instructions. S03/S06 name only the assigned entrypoint and its required sources; S10 names both without imposing a design sequence.

The helper pins the original public case manifest, complete frozen A file/link identities, frozen skill-creator instructional files and restored original display assets, and common format document. Preparation records source file modes too. Generic path, inventory, cache, and exclusive-output checks are reused from `prepare_control_consumers.py`; C-specific allocation checks are used only for the twelve original C identities. Existing source/cache bytes survive. Resource files and modes are compared before/after copying. An unexpected link, unsupported file, non-cache checkpoint-omitted resource, changed source, or existing/partial destination stops staging without cleanup. Exactly one supplied Skill is required, matching these briefs and the control helper; multiple outputs require explicit reconciliation, not selection of a favorable package.

Creator preparation writes only creator tasks and coordinator schedules/assignments. It does not read or materialize consumer cases. Consumer preparation requires an explicitly completed creator, unchanged prompt/input/modes, its public handoff, and a preserved format observation of the same generated package. A format failure is retained and does not silently remove its planned consumers or authorize repair. Only after these checks does it freeze the original Skill and copy the two independently frozen raw control cases. Path substitutions are recorded; the S06/S10 interfaces retain original public bytes/modes. S06 hidden fixtures and setup evidence remain outside consumer task folders.

The narrow F-only S06 adapter preserves the reviewed `init`/`describe` observations and read-only, transaction-consistent native SQL snapshots. The existing state helper is intentionally not reused or monkeypatched because its ID checks and recovery bindings are C-specific. New databases use exclusive `F-Uxxx-ledger-state-*` directories beside the assessment. Final SQL represents committed logical state, not byte-identical SQLite or a complete call history. No recovery mechanism is added.

## Coordinator use and public evidence

Run from the assessment root with `python3 -B`:

```sh
python3 -B prepare_focused.py creators
```

Checkpoint preparation before first execution. Launch fresh creator contexts using only each task's `prompt.md` and the requested schedule configuration. Preserve actual observable configuration, public commands/results and the final response without private reasoning. Keep `trials/focus-NNN/execution-note.md` as the creator's own report; copy the actual completion response to the coordinator-only `focused-public/focus-NNN/final-response.md` without rewriting its content. Record explicit completion with the existing `record_status.py` in `focused-list.tsv`. Then, for the completed IDs only:

```sh
python3 -B prepare_focused.py validate focus-001 focus-002
python3 -B prepare_focused.py consumers focus-001 focus-002
```

Validation is the same pinned physical-format check used for C, not semantic or business validation. Its report, package hashes/modes, public handoff hashes, and cache exclusions are bound into the freeze record. Original extra demonstrations and verification work remain in the creator workspace for checkpointing and independent evidence packaging; they are not supplied to consumers. Non-text verification artifacts may need the existing explicit preservation route before checkpointing; this helper never silently omits them.

After successful preparation, record the printed F consumer IDs as `prepared` in `focused-consumer-list.tsv`, checkpoint, then launch fresh sol/high consumers using only their supplied prompt, Skill, and task inputs. Preserve each `answer.md`, `execution-note.md`, full final task files, and the actual final response at coordinator-only `focused-public/F-Uxxx/final-response.md`. Record explicit consumer completion. For completed S06 applications, preserve final state promptly:

```sh
python3 -B prepare_focused.py snapshot F-U009 F-U010
```

This writes exclusive `final.sql`/`final.json` evidence anchored to the original setup and initial snapshot. Preserve public completion records and full observed resources before blind grading, including changes/deletions/additions, modes, creator-reported checks, and non-Skill deliverables. A helper success, note, or exit zero is not an adequacy judgment. Missing, interrupted, failed, and not-run slots remain in their fixed denominator; distinct retries preserve originals and follow the authorized retry budget.

The remaining C-U133–136 and C-U141–144 use their existing preserved assignments and control workflow. This helper does not stage them again. Blind paired grading, independent second grades/adjudication, the three A meaning reviews, and the final chart report are coordinator work after these preparations. Retain the recovered-C provenance and noncontemporaneous comparison limitations; this three-family/two-configuration comparison cannot satisfy the original broad A/B release gates.

The helper was added without preparing an assignment, copying a consumer case, running a physical validator or business API, or launching a trial. Read-only checks on 2026-09-08 passed: Python compilation without bytecode output, `--help`, all twelve original C pairing identities, all 70 frozen A file/link identities and nine common-aid files, and exact prompt equivalence after removing the assigned ALPS addition and reversing the task-directory substitution. Fixed schedules contain 12 creator cells and 24 consumer slots. These checks are preparation evidence, not model or business results. The F-only state setup/snapshot path has not been exercised; the coordinator should review that concrete adaptation before consumer preparation.
