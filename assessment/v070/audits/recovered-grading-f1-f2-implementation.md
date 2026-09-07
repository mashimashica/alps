# Follow-up implementation for recovered creator findings F1 and F2

The two evidence-admission defects identified in `audits/recovered-grading-review.md` have been corrected and are ready for independent follow-up. This is a new implementation observation. The original implementation note and the review containing the reproduced failures remain unchanged; this report does not replace their findings or approval boundary.

No real grading packet was created or edited. In particular, the already prepared S06-P01/P03 packets were not modified. No business command, Skill edit, original trial-file change, ledger update or Git operation was performed by this correction task.

## F1: canonical public-note identity

All four recovered creators' actual `trials/<creator>/execution-note.md` files must now be regular files with the reviewed bytes and applicable mode 0644. The two evidence paths remain distinct:

| Creators | Identity used |
| --- | --- |
| control-069/control-070 | The committed note hashes corroborated by the unchanged relays and recorded in the independent review: `358a9face475b70dae4d513206b215fa3495432344b129968a47646d880a4fb6` and `780adc079178f47a0e8945c1c76a48e338122a5fea62962a6948638458202fe9`. |
| control-071/control-072 | The exact note entries and placement modes in the already pinned rematerialization record: `a0afe632487602bad243bd24e071b88ad803812615a8606de7f72eb4d3569626` and `eb833ccecc88626b8f52a2ece1b1393d9add0c6e0247dd24d02d58215c397313`. |

The selected canonical note, its expected hash/mode and its identity source are now part of the recovery plan/provenance. No evidence pin or rematerialization record was changed to admit different text.

## F2: closed recovered deliverable inventory

The canonical deliverable tree must contain exactly the reviewed three package resources, with their fixed hashes and current recorded modes. For control-071/control-072, the rematerialization entries must cover exactly those resources and the separate note, and their hashes/modes must agree. The frozen package is also checked as a closed tree. Unknown files, extra or missing directories, missing/changed resources, wrong resource modes, symlinks and nonregular entries are rejected.

The existing narrow Python-cache convention remains available only for regular `.pyc` files immediately under `__pycache__`. Such canonical-source caches are recorded by hash and mode in the plan and excluded from the candidate copy; their original bytes are not claimed saved. Non-cache content under that directory is rejected. A cache addition or modification after planning changes the recorded inventory and stops copying. Frozen packages do not acquire a new cache exception.

Recovered creators now use a dedicated checked candidate-copy branch. It copies only the planned frozen package resources, the checked canonical public note and the filtered recovery attachment. It never passes through the generic `other-creator-deliverables/` branch. An unknown deliverable therefore causes a refusal instead of being silently dropped or admitted.

The full selected recovery plan is revalidated before candidate creation and around attachment creation. Every copied source is checked as a regular file with its planned hash/mode, and the destination is verified against those planned values. The post-copy check also covers canonical resources that were checked for identity but not used as the frozen-package copy source. Examined source changes during copying stop the operation and leave partial output for reconciliation; existing partial destinations cannot be replaced automatically.

Non-recovered creators retain their original copy/preservation branch, including ordinary additional deliverables. Consumer supplementation, native restored-path bindings, grading criteria, allocations, denominators and missing-observation rules are unchanged. The shared planned-copy helper now explicitly rejects a nonregular source before reading it; existing consumer evidence layouts and pins remain unchanged.

## Verification

`python3 -B -m unittest test_recovered_control_grading test_recovery_ledger_binding -v` passed all **39 tests**, including the previous 30 and nine focused follow-up tests. The new cases cover both committed-original and rematerialized provenance paths:

- Changed, missing and wrong-mode public notes; missing, changed and wrong-mode canonical resources.
- Unknown deliverable files and empty directories, symlinks and a FIFO.
- Complete checked copies for all four candidates, with expected note/package hashes and modes.
- Source-note/resource/mode or extra-file changes after planning.
- Mid-copy insertion of an extra deliverable and mid-copy changes to a canonical note or selected frozen file's bytes/mode; partial-output preservation and refusal to overwrite it.
- Explicit recording/exclusion of a permitted runtime cache, rejection of a changed cache after planning, and rejection of non-cache content in its place.
- Execution of the actual creator-copy loop selected from `prepare_control_grading.main`'s AST, showing that both original F1/F2 mutations now fail before candidate output for both provenance paths.

Additional disposable execution of that actual loop succeeded for all four valid recovered candidates, each containing eight output files: the public note, three package resources and four recovery-attachment files. A baseline-versus-current ordinary creator-loop comparison matched all five output files in bytes and modes, including an extra ordinary deliverable. These checks isolate actual copy-loop behavior; they are not complete real packet construction or business applications.

Read-only planning accepted all four current real canonical creator versions and their expected note hashes. `python3 -B checkpoint.py verify` passed. Whitespace checks emitted no diagnostics; no-index diff checks returned 1 for differing contents.

## Current identities

| File | SHA-256 |
| --- | --- |
| `recovered_control_grading.py` | `8fd7bc985792778c457732df8a24a9f03c011e151f434475350f3261e5bedfe6` |
| `prepare_control_grading.py` | `8b124cc5959a3408d649d1e904f3a37850bde037be4a95def66ed33c871e1763` |
| `test_recovered_control_grading.py` | `cc1d81eb9be571c20a7d8aa3573f22dd25bf8b28cee8a9011e27b441608ad027` |
| Preserved original implementation note | `2a6c5e95d7525074d82f5bee9116f531b4e7247513a532fdbaba7fbb9a0490d3` |
| Preserved independent failing review | `e214d9e280a547965a2b001d7da1379ba2ee24c29ddd94012cb051f7de24545a` |
| Unchanged consumer provenance manifest | `4a24e1cb17327ea2b05e11b9c8cabcd2324e6b0ec6f9a8f66bbadadd322bf35b` |
| Unchanged creator recovery-freeze companion | `03cd21ec820654b6978ea75c903bde1863b1cc625614fe5bbf1859d693f1d402` |
| Unchanged `recovery_ledger_binding.py` | `3a762fb2dcc9d8c5bf9a7288cef5bb672ad2e2b0c653eaaa04579bfb8477fc9b` |
| Unchanged `control_ledger_state.py` | `86a925979d855b6c11d8297c37663b088331571d6a7317863664b7b17cea4914` |
| Unchanged `checkpoint.py` | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |

Independent follow-up and preservation of the accepted implementation remain required before constructing packets containing these recovered creators. No full packet, adversarial concurrent-writer protocol, or filesystem transaction guarantee was tested. The coordinated serial workflow remains the applicable execution condition; the evidence-admission checks do not prove business correctness or change any release boundary.
