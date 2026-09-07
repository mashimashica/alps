# Independent review: creator input cache handling

**Disposition: no blocking finding for the narrow C061 correction.** Record the added cache separately and continue assessment preparation without rerunning the creator or repairing its Skill. An added Python cache with unchanged supplied source is not evidence that the supplied source was rewritten. This conclusion concerns assessment bookkeeping, not business adequacy or a grade.

## Evidence checked

Read only the three packaging/checkpoint helpers, the required `control_ledger_state.py` import, the C061 observation, assignment, prompt, input tree and execution note. Actual checks used new disposable copies under `grading-work/control-input-cache-review/.local/run-3jvqxoxs`; no original trial or consumer preparation was run.

The copied supplied inputs matched the assignment exactly:

| File | SHA-256 |
| --- | --- |
| `input/brief.md` | `284eab48172c8b996d5eb3218590fb453c1e24f5b532f9d4457bda99fb38485e` |
| `input/release_tool.py` | `939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577` |

The prompt matched its assigned hash, `ab875c9f2790fcbcd789d368e605ff792c1fbd528d5353b5cad4939e4633725b`. The only additional regular input file was `__pycache__/release_tool.cpython-312.pyc`, hash `817e07c25329c62c67ad09f7db52c4dde4222c6d3f42733d40a7d0228682b44b`, matching the observation. The public execution note reports `python3 -m py_compile input/release_tool.py`, exit 0. That report is consistent with the cache, but its production history was not independently attested.

## Findings

- **Original byte identity stays mandatory.** `creator_input_caches()` first compares every expected file hash with the complete regular-file inventory, then classifies additions. Missing, renamed or changed originals still fail, including an original cache if it was already part of the supplied manifest. In `main()`, expected originals are derived from the verified public bank, compared with the creator assignment, and the original prompt hash is checked separately.
- **The exception is confined to added regular `.pyc` files directly inside a directory named `__pycache__`.** Other added regular files fail. `file_hashes()` checks paths for symlinks before hashing and rejects unsupported filesystem entries. Refusals preserve the files for reconciliation; preflight occurs before freeze or consumer writes.
- **Original evidence is retained.** The new function only inventories and hashes. The freeze manifest records `creator_input_added_runtime_cache_sha256` separately from supplied Skill resources and Skill cache exclusions. Copying preserves ordinary resource bytes/modes and leaves original caches in place. Consumers receive the frozen Skill resources and their prescribed inputs; the S10 interface is copied from the frozen public source, not the creator's modified input directory.
- **Later packaging and checkpointing remain compatible.** Consumer assignments hash the entire freeze manifest, including the new cache field. Blind grading checks that binding and uses frozen original creator inputs, while cache observations remain external to the blind packet. The synthetic tamper test confirmed that changing only the recorded creator-input cache hash causes blind preparation to refuse. `checkpoint.export()` retained the external manifest and original source, and excluded raw `__pycache__` payloads. The manifest accurately avoids claiming that the raw cache bytes are durably preserved.

## Checks performed

Command: `python3 -B grading-work/control-input-cache-review/run_review.py`, Python 3.12.13, **exit 0; 25 checks passed**. The executable check script and `grading-work/control-input-cache-review/results.json` retain the checks and observations.

The checks covered unchanged input with/without a cache; altered, missing and renamed originals; a changed originally supplied cache; added ordinary files, misplaced/nested `.pyc`, non-`.pyc` cache-directory content and uppercase `.PYC`; original/cache/dangling/directory symlinks; a cache-named FIFO; and the classification limits below. Rejection checks compared fixture inventories before and after each call.

A synthetic S10 packaging fixture exercised whole-helper preflight refusal before writes, successful two-consumer preparation, refusal to overwrite existing preparation, freeze-manifest tamper rejection, successful blind packaging, and checkpoint export. Assertions checked original input/Skill preservation, resource hashes, executable mode, cache omission and retention of the separate cache hash record. Finally, all read original evidence/helper bytes and file modes, plus the original input inventory, matched their initial snapshots.

## Limits

Cache classification is based on a regular file's path and suffix; it does not validate bytecode content or prove the command that created it. The checks confirmed that an opaque `.pyc` is accepted and an added empty directory is not inventoried. Original creator-input identity covers file paths/bytes, not directory metadata or original input modes, and preflight is not an attestation against concurrent writers. These limits do not change the observed C061 bytecode-only case.

The integration fixture used substituted identity constants in memory, synthetic schedules/banks/guidance, one creator and two placeholder completed applications. It tests packaging mechanics, not the actual fixed allocation, all families or a real four-creator packet. No business source/cache was executed, no target Skill was inspected or judged, and no live packaging, remote checkpoint save or creator retry occurred. The observation's prior physical validator result, earlier refusal and sibling-consumer status were not independently rechecked under this review's read boundary.
