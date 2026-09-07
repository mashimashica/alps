# Pending S06 recovery binding implementation

The implementation is ready for independent review. No real C-U094–096 state was restored, no business API operation was invoked, and none of the three consumer contexts was resumed by this work.

The recovery basis is `audits/environment-restoration-review.md` and the preserved evidence at commit `75c0ea9bddf379c5e1803e4c0114ba5b47c871d8`. This is an assessment-only infrastructure change. It does not change ALPS, an evaluated Skill, trial assignment, grading criterion, or retry accounting.

## Behavior

`recovery_ledger_binding.py` accepts only C-U094, C-U095 and C-U096. Their exact preserved assignment SHA-256 values are pinned in the helper. Each assignment anchors its original setup, initial SQL and initial metadata. The helper verifies those hashes and identities, the original state-path substitution, the prescribed fixture/interface identities, and the original successful setup observations.

Before writing, it requires the matching mutable ledger row to remain `prepared`; verifies the original prompt and every copied resource byte/mode; and refuses existing application files, a final snapshot, an original native-state directory, a binding record, or any existing recovery directory for that consumer. A completed consumer cannot be restored. Symlinks, noncanonical paths, another consumer's destination and an existing or partial destination are rejected.

The destination must be a new `C-U094-ledger-recovery-<lowercase-name>` directory beside the assessment, with the corresponding consumer prefix for C-U095/C-U096. The directory and `ledger.sqlite` are created exclusively, with modes 0700 and 0600. Only the assignment-anchored SQL is loaded. In-memory preflight and the new native database must both pass `quick_check`, exact `iterdump` equality, full prescribed record equality, matching snapshot, tranche 1 and zero used calls. No `init`, `page`, `describe`, or `grant-tranche` business command is called.

The separate `recovery-bindings/<consumer>.json` records the original path, new path, assignment and source evidence hashes, restored logical SQL hash, newly observed binary hash, initial snapshot/record/quota observation, SQLite version and UTC observation time. The original setup, request, prompt and initial snapshot are not rewritten. A failed partial restoration is retained and prevents another automatic restoration, including one at a different new destination.

`control_ledger_state.py` reads this explicit binding for later snapshots. Final metadata keeps the actual new `state_path`, adds `original_state_path`, and pins the separate recovery record's path and hash. Original initial metadata keeps its original identity. Ordinary snapshots with no recovery record retain their prior behavior.

`prepare_control_grading.py` checks both original and recovered snapshot identities and copies the recovery record beside the original setup observations into the relevant S06 application packet. Validation does not require the live database to survive after its final native SQL has been captured. Existing grading guidance and the common evidence-boundaries text remain unchanged.

## Verification performed

`python3 -B -m unittest test_recovery_ledger_binding -v` passed all 11 disposable component tests. They cover:

- Exact restoration of all three preserved initial states, unused quota and restrictive native file mode, while retaining the copied original evidence unchanged.
- Rejection of another/completed assignment, altered assignment/source hashes, wrong snapshot/tranche/used quota, a changed prompt and existing application evidence.
- Preservation of existing and failed partial restorations; rejection of symlink and cross-consumer destinations.
- An actual disposable final-snapshot capture after a local fixture-only quota change; grading validation of both paths and the binding hash; rejection of missing/tampered bindings; an exact binding copy; and grading validation after the disposable native database is removed.
- Unchanged original-path validation for an unrecovered consumer.

The tests copy the original evidence into temporary directories. Their fixture-only SQL changes are not consumer trials, recorded application results, or calls to the business API. They do not repair or run evaluated Skills.

`python3 -B checkpoint.py verify` passed. Read-only comparison against the immutable checkout confirmed that the 32 original assignment, setup, prompt, initial snapshot and copied-resource files used by C-U094–096 retain exact bytes and modes. Read-only verification confirmed no real recovery binding or real recovery directory had been created.

Whitespace checks of each of the four owned Python files against its baseline or `/dev/null` produced no whitespace diagnostics. `git diff --no-index --check` returned 1 because the compared contents differ.

## File identities

| File | SHA-256 |
| --- | --- |
| `recovery_ledger_binding.py` | `3a762fb2dcc9d8c5bf9a7288cef5bb672ad2e2b0c653eaaa04579bfb8477fc9b` |
| `control_ledger_state.py` | `86a925979d855b6c11d8297c37663b088331571d6a7317863664b7b17cea4914` |
| `prepare_control_grading.py` | `d7005df01a39597cebe5df97f6004ba7da37c10a9915198caccb412b8bc0e6fa` |
| `test_recovery_ledger_binding.py` | `51747c34d5d93aa25847f07e62a93c261963ab4de9f6ec4b13340bc574de0aef` |
| Unchanged `checkpoint.py` | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |

## Remaining boundaries

The coordinator must independently review and preserve these helper identities before actual use, then preserve the resulting recovery records before resuming the retained contexts. The minimal continuation notice should replace only the old native state-path literal with the recorded new one and retain every existing task condition. No original prompt/request rewrite is needed.

No full S06-P01/P03 grading packet was generated: their consumers and missing-evidence packaging remain separate prerequisites. This change does not recover completed consumers' missing artifacts, manufacture historical final-state captures, or add a supplemental-evidence packaging route. It does not support another restoration after this bounded recovery or resolve the separate candidate progression gate.
