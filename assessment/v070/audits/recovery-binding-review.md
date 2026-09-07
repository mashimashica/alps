# Independent review of pending S06 recovery binding

**Decision: approved for the bounded, serial restoration of C-U094, C-U095 and C-U096 using the helper identities below. No blocking defect was found within that scope.** Preserve this review and the implementation identities before actual restoration; preserve each resulting recovery record and its new native-state observation before resuming the corresponding retained context. This review performs neither action.

The approval depends on the prior independent finding that these three original contexts were interrupted before reading task resources or performing business operations. A `prepared` ledger row and absent output files alone cannot establish that history. If the retained context or that history differs, this approval does not apply.

Review observation: 2026-09-07, with final real-state preflight at `2026-09-07T23:14:47.986733+00:00`. Working root: `/workspace/scratch/a75c3a6d9076/alps-v070-assessment`. Preserved baseline: `/workspace/scratch/a75c3a6d9076/alps-evidence-recovery-75c0ea9/assessment/v070`, at verified Git HEAD `75c0ea9bddf379c5e1803e4c0114ba5b47c871d8`. SQLite used for the disposable checks: `3.53.1`.

## Findings

1. **Restoration is anchored to the original assignment and exact initial evidence.** `recovery_ledger_binding.py` permits only the three pinned assignment SHA-256 values. It validates the assignment's setup, initial SQL and initial metadata hashes; consumer and S06 identities; original path and request substitution; fixture and interface identities; and original setup observations. It restores the anchored SQL into memory before creating a native file. The checks require exact dump equality, integrity, all prescribed records, the fixture-derived snapshot, tranche 1 and zero used calls. Successful original setup is evidence of initial readiness, not inferred application success.

2. **The pending assignment and its resources are preserved.** Restoration requires one matching `prepared` ledger row, the original creator/case/variant, the original prompt hash, and all copied resource hashes and modes. Existing application files, final snapshot evidence, original native-state directories, recovery records and consumer-specific recovery destinations stop restoration. No restoration path writes setup, request, prompt, initial snapshots, assignments, ledger status, evaluated resources or their original hashes. The current real folders contain exactly the expected resource files and prompt, with no unusual filesystem entries.

3. **New native state is allocated separately and interrupted writes fail closed.** The destination is canonical, beside the assessment, and uses the matching `C-Uxxx-ledger-recovery-...` prefix. An exclusive directory and exclusive `ledger.sqlite` creation prevent replacement of an existing destination. Observed modes were 0700 and 0600. A failed connection after empty-file creation and an interrupted recovery-record write both retained the partial evidence and prevented a second restoration at another destination. Neither case generated a usable real or disposable final metadata record through the snapshot helper. There is no automatic cleanup/retry loop.

4. **The recovery record distinguishes original evidence from new observations.** It retains the original and restored paths, pinned assignment and source evidence hashes, restored logical SQL hash, newly observed native binary hash, initial state observation, SQLite version and current UTC time. The recorded binary hash identifies the newly created SQLite file; it does not claim recovery of the lost original SQLite bytes. The identity loader validates the central source/path/state bindings and the UTC timestamp form. It need not read a live database when validating saved grading evidence.

5. **Snapshot integration retains both identities without rewriting initial metadata.** The change to `control_ledger_state.py` chooses the explicit restored path for a later snapshot and records `state_path`, `original_state_path`, `recovery_binding_path` and `recovery_binding_sha256`. Original initial metadata retains its original path and bytes. Missing, partial, inconsistent or cross-consumer bindings cannot validate a recovered final. Native capture still uses a consistent read transaction, `quick_check` and exclusive new SQL/JSON evidence files. An independent disposable capture left the native binary hash unchanged. Capture records observed state; it does not prove completion, requested-task adequacy or business success.

6. **The grading change carries the recovery evidence into the application packet.** The original initial-evidence hash checks and allocated original-path check remain. Both initial and final metadata then pass the recovery-aware identity validator. The S06 copy branch copies the original setup, native snapshots and the separate recovery record. Independently executing that unchanged branch against disposable files preserved the exact record digest referenced by final metadata, both paths and the original initial observations. It worked after removing the disposable live database. The baseline grading guidance, evidence-boundaries text and business criteria are unchanged by this implementation.

## Checks actually run

The source review covered `audits/environment-restoration-review.md`, `audits/recovery-binding-implementation.md`, the complete new binding helper and supplied test file, the snapshot helper, the grading helper and its diff against the preserved baseline, and the relevant resource/path/copy helpers in `prepare_control_consumers.py`. No evaluated Skill instructions or business results were used to judge the implementation.

`python3 -B -m unittest test_recovery_ledger_binding -v` passed all **11** tests. These exercised all three exact initial restorations; protected assignment/source hashes; wrong snapshot/tranche/quota rejection; changed prompt and existing output rejection; existing/partial destination preservation; symlink and cross-consumer paths; later snapshot identities and offline validation; copied binding identity; missing/tampered bindings; injected native validation failure; and unchanged unrecovered snapshot validation. The suite's local quota update was confined to its disposable component fixture and made no business API call.

An additional one-off Python harness ran these **14 independent checks**, each using temporary copies and cleaning them afterward:

| Check | Observed result |
| --- | --- |
| Ledger status `started` | Rejected before creating a native directory. |
| Ledger status `interrupted` | Rejected before creating a native directory. |
| Ledger status `completed` | Rejected before creating a native directory. |
| Existing partial `final.sql` | Preserved; restoration rejected. |
| Changed copied request | Rejected by original resource hash. |
| Changed copied API file mode | Rejected by original resource mode. |
| Added dangling symlink in consumer resources | Rejected as existing application evidence. |
| Symlinked recovery-record parent | Rejected without writing through it. |
| Relative destination | Rejected as noncanonical. |
| Uppercase destination suffix | Rejected by destination grammar. |
| Destination inside the assessment | Rejected by parent-location constraint. |
| Injected SQLite connection failure after exclusive file creation | Zero-byte native file retained at mode 0600 inside mode 0700 directory; different-destination retry rejected. |
| Injected interrupted JSON record write | Partial JSON and native database retained; different-destination retry and final snapshot capture rejected. |
| Actual S06 grading-copy branch after deleting the disposable live database | Exact setup, initial/final SQL and JSON, and recovery record copied; SQL hashes, both paths and binding hash validated; original copied evidence unchanged. |

For the last check, the harness selected the actual S06 copy `if` node from `prepare_control_grading.main` using Python's AST and executed that unchanged code with disposable source/destination paths. It did **not** invoke the complete grading-packet constructor or bypass the real packet's missing-evidence gates. The full constructor and its surrounding preflight were reviewed statically. The disposable final was an actual read-only snapshot of a newly restored fixture, labelled only for this component check; it was never added to real consumer evidence or represented as an application completion.

Read-only identity verification compared **34 unique original files** against both the preserved filesystem and their exact Git blobs/modes at the baseline commit: the three assignments, setups, prompts and initial SQL/JSON pairs, every copied request/API/Skill resource, and the two prescribed fixtures. All comparisons passed. The 32 per-consumer files and two shared fixtures account for the total. Original content was hashed/copied for identity checks; no evaluated business API or Skill script was executed.

At the final real-state preflight, all three relevant ledger rows remained `prepared`, with their original creator/case/variant/model/effort. Their original native directories, recovery directories, binding records and `final.*` snapshots were absent. The four reviewed Python implementation/test hashes still matched. These are presence and identity observations; the review did not create any real consumer state.

## Reviewed file identities

| File | SHA-256 |
| --- | --- |
| `recovery_ledger_binding.py` | `3a762fb2dcc9d8c5bf9a7288cef5bb672ad2e2b0c653eaaa04579bfb8477fc9b` |
| `control_ledger_state.py` | `86a925979d855b6c11d8297c37663b088331571d6a7317863664b7b17cea4914` |
| `prepare_control_grading.py` | `d7005df01a39597cebe5df97f6004ba7da37c10a9915198caccb412b8bc0e6fa` |
| `test_recovery_ledger_binding.py` | `51747c34d5d93aa25847f07e62a93c261963ab4de9f6ec4b13340bc574de0aef` |
| `checkpoint.py`, unchanged from baseline | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |
| `audits/environment-restoration-review.md` | `b24460ae1ebd8813cd67e378d894e7ef97ed0b427c503f2e80345484eeff7890` |
| `audits/recovery-binding-implementation.md` | `c5e268e89e2a989634e79ead76b5e70e3a8f9bf7f6f2b608aba3926bb53f724b` |

For comparison, baseline `control_ledger_state.py` was `d882ca0323dd6e8887017b74ea1dc7adc06bd8cd1c0b3b92deda00c26932094d`; baseline `prepare_control_grading.py` was `d0af475ae5f6809273232c5b49800772845e2bfbff1b71d33880892f485c0c1f`.

| Consumer | Original assignment SHA-256 | Initial SQL SHA-256 |
| --- | --- | --- |
| C-U094 | `b2f7ff3927349317b1530a8bf60ce8104a598f8126232fef8b722d8476e680da` | `cff24d0d1e625ef2c10c6cb417f2322f1f11fd4f3693ae295d5d5641990b47b7` |
| C-U095 | `d9e3317c51a2d27f5b996a50f6eb68b28a4fd777d03cef2dcc00bcf62e4f5554` | `1206581aaa26d95a4831a91f82dd1b59f06cfc56195294559db2af8192f63204` |
| C-U096 | `b15900cd1edc6db475aedc5ea7b3dd3211ff22d68a0af781cf7cc262cf833ec4` | `cff24d0d1e625ef2c10c6cb417f2322f1f11fd4f3693ae295d5d5641990b47b7` |

| Consumer | Original setup SHA-256 | Initial metadata SHA-256 |
| --- | --- | --- |
| C-U094 | `599fc130eab77ddaabb2660901fcada6bdfa79a8dbd9d56f04ca3a4a246440c2` | `ce00cc941e98f5366cd129a928f00488a4f6bef08d66a05c591b30ad69e992e0` |
| C-U095 | `1933b963dcc6101cc74d8aaf4e1337d145a2e80cd197ab794d02d9f32e728262` | `2473f55e0da914fdbebd9e7462a883502bd62dd839b674efc47d064f157ae14c` |
| C-U096 | `bca0221dd3382c08a41727c1462c13a4e9ef92645536ec7e3a27b748f72fa167` | `8aa8b3804005ff82ac290cdedba4839d1b8f172f3d4cd1a0446eaaea177e7a3c` |

The original paths remain:

- C-U094: `/workspace/scratch/a75c3a6d9076/C-U094-ledger-state-ucpf2ya_/ledger.sqlite`
- C-U095: `/workspace/scratch/a75c3a6d9076/C-U095-ledger-state-6smwuab_/ledger.sqlite`
- C-U096: `/workspace/scratch/a75c3a6d9076/C-U096-ledger-state-tl_2q93_/ledger.sqlite`

## Approved and blocked scope

Approved: one serial invocation per named still-pending original attempt, using the exact assignment-anchored initial SQL and an exclusive new directory accepted by this helper; preservation and verification of the resulting recovery record; then the retained context's minimal state-path continuation after the required recovery checkpoint. That continuation may replace only the obsolete state-path literal and must preserve the original prompt/request and every task condition. Later native snapshots and grading copies may use the reviewed integration while retaining original and restored identities.

This is approval for a coordinated serial procedure. No concurrent restoration stress test was run, and the helper does not provide a cross-process transaction spanning its preflight, directory creation and binding write. Do not run competing restorations or a consumer against the state while recovery is being created and preserved. A partial restoration remains an explicit reconciliation item; it is not permission to delete evidence or restart automatically.

Blocked or outside this approval: restoration of any completed consumer; other consumer IDs; a replacement context or retry; another restoration after a partial/successful one; `init`, `page`, `describe` or `grant-tranche` as part of recovery; quota/snapshot/data changes; rewritten original setup/request/prompt/hash evidence; synthetic historical final metadata; inference of business success from restored state; missing completed-consumer evidence repair; supplemental packaging; complete S06 grading packets; candidate progression, retry/reserve accounting or release decisions.

No real consumer was restored or resumed, no business API command was executed, no completed task was rerun, no other grades or business results were inspected, and no implementation or original evidence file was edited by this review. The only retained write is this report. Publication/checkpoint execution and any actual recovery remain the coordinator's responsibility.
