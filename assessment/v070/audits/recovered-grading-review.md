# Independent recovered grading implementation review

**Decision: approve the fixed C-U084–093 consumer supplemental-evidence packaging path at the identities below, subject to the normal complete-packet gates and a verified checkpoint. Block packet construction involving recovered creators control-069–072 until their canonical public notes and closed deliverable inventories are checked against the reviewed evidence. The implementation is not approved as a whole.**

The block is an evidence-admission defect, not a finding that the current real creator notes are corrupted. All four current notes still match their reviewed relays. The consumer supplement checks, ordinary copy path and previously approved restored-path integration passed the checks performed here. The bounded creator defect can be corrected without changing a generated Skill, business criterion, trial identity or grade.

This review read the implementation note, complete new helper, complete changed grading helper, their relevant diff against the retained `75c0ea9bddf379c5e1803e4c0114ba5b47c871d8` baseline, both supplied test files, the approved recovery-binding review/helper, and the pinned consumer/creator/request recovery provenance. All new writes other than this report were confined to disposable test directories and cleaned by their fixture cleanup. No real packet, actual consumer workspace change, real native-state operation, business API call, trial execution, delegation or Git write occurred. Read-only real-evidence planning was performed; it wrote no packet.

## Blocking findings for recovered creator packaging

### F1 — changed canonical public note is accepted

`recovered_control_grading.py:286` validates the recovery companion and its referenced records, frozen resource hashes/modes, relay, format report and reconstructed consumer assignments. The selected rematerialization entries at line 312 are copied into provenance, but the current canonical note bytes are not compared with their recorded identity. `prepare_control_grading.py:245` then copies `trials/<creator>/execution-note.md` directly to `creator-reported-checks.md` through the ordinary copy helper.

In an independent disposable C071 fixture, I kept the pinned companion, relay, format report, canonical freeze, resources and assignments unchanged, supplied the ordinary creator deliverable tree, and replaced only its disposable `execution-note.md` with `UNREVIEWED REPLACEMENT CREATOR NOTE\n`. `plan_creator` accepted it. Executing the unchanged actual creator-copy loop selected from the grading helper's AST copied that replacement to `creator-reported-checks.md` and also attached the pinned recovery provenance. Captured result:

```json
{"check":"changed recovered creator public note","plan_accepted":true,"changed_note_copied":true,"attachment_still_asserts_recovery":true}
```

The full constructor's surrounding preflight checks that a note exists and is a regular permitted path; it has no intervening check against the known note identity. Completing the fixed consumer gates would not supply that missing check. The disposable loop execution isolated the copy defect; it was not a full real grading-packet invocation.

For C071/C072, the pinned rematerialization record already identifies the expected notes. C069/C070 have committed originals independently corroborated by their unchanged relays. The checked real note identities are:

| Creator | Current note SHA-256; also matches the complete reviewed relay body |
|---|---|
| control-069 | `358a9face475b70dae4d513206b215fa3495432344b129968a47646d880a4fb6` |
| control-070 | `780adc079178f47a0e8945c1c76a48e338122a5fea62962a6948638458202fe9` |
| control-071 | `a0afe632487602bad243bd24e071b88ad803812615a8606de7f72eb4d3569626` |
| control-072 | `eb833ccecc88626b8f52a2ece1b1393d9add0c6e0247dd24d02d58215c397313` |

### F2 — an unknown recovered creator deliverable is admitted

The same selected recovery plan does not compare the canonical creator deliverable inventory with the complete reviewed recovered inventory. The unchanged generic branch at `prepare_control_grading.py:255` copies any additional root deliverable into `other-creator-deliverables/`.

A second independent disposable C071 fixture retained the genuine note and pinned package, then added only `deliverables/unreviewed-summary.md` containing the synthetic text `SYNTHETIC OTHER-GRADE/MODEL-MAPPING SENTINEL\n`. `plan_creator` accepted the fixture, and the actual creator-copy loop copied the added file into the packet. Captured result:

```json
{"check":"unknown recovered creator deliverable","plan_accepted":true,"unreviewed_extra_copied":true}
```

No real other grade or model mapping was used in this test. The sentinel demonstrates that the otherwise careful filtered recovery attachment does not control this second route into the same recovered candidate's packet. The reviewed C069–072 evidence describes their complete three-file packages and separate notes, with no extra demonstration; a newly appearing deliverable requires reconciliation, not automatic admission under that recovery provenance.

The minimal correction is to check all four canonical public-note identities and the closed canonical recovered creator deliverable/resource inventories, including applicable current modes and permitted cache treatment, against their reviewed sources. Bind the selected canonical observations into the recovery plan and recheck their bytes/modes when copying. Reject missing, changed, unknown or nonregular entries and changes after preflight; preserve partial output rather than overwrite it. Keep the ordinary preservation behavior for non-recovered creators. Add focused disposable tests for changed notes, unknown deliverables, missing or changed known resources/modes, and alteration between planning and copy. No implementation edit was made by this reviewer; a separately reviewed follow-up is required.

## Approved consumer supplemental path

The exceptional route is selected only for the exact completed original S06 IDs C-U084–093. It is not a fallback for any ordinary packaging error. All ten assignments are pinned, and the normal constructor still checks the frozen allocation, schedules, family case bank/oracle, creator completion and freeze, consumer completion and identity, original prompt, copied mode-key coverage, original setup/initial evidence and native identity. The supplemental route requires the exact 32-file reviewed manifest and inventory; unknown IDs, altered manifest content and missing or changed files fail before packet creation.

Each source relay is checked against its recorded SHA-256 and Git blob identity. Extracted text is checked against the exact recorded inclusive source lines. Matched SQL is checked against the committed source content and blob. The current source consumer folders must contain exactly the assignment-backed prepared resources, original prompt, and the specifically pinned surviving observations. Unexpected files, a new original `final.*` snapshot, changed original bytes or modes, or a completed-consumer recovery binding require reconciliation. A changed C084/C085 original cannot silently fall back to its relay.

The generated layouts honestly distinguish:

| Evidence | Packet representation |
|---|---|
| Original prompt and restored prepared resources | `prompt.md`, `prepared-input/`, `prepared-skill/`; no final resource-inventory assertion |
| Surviving C084/C085 answer, note and checkpoint | `original-public-observations/`, `original-work-evidence/` |
| C086–093 extracted public observations | `recovered-public-text/` with the unchanged source relay and selected provenance |
| Available checkpoint renderings | `recovered-work-evidence/`, retaining the specific serialization limitations |
| Original initial SQL/metadata and setup | `committed-initial-state/`, `setup-observations.json` |
| Nine historically hash-matched SQL contents | `logical-state-supplement/`; explicitly not original final metadata or a new final capture |
| Remaining gaps | `evidence-availability.md` and filtered recovery provenance |

No `observed-final-skill/`, `final-input-state/`, fabricated final-resource comparison or original per-trial `final.json` is generated for these ten applications. The same requested-task criteria, denominators and missing-observation rules remain in force. Packaging labels do not assign grades or automatically invalidate applications.

C-U092's separately pinned proof is integrated correctly. The helper requires the exact proof, its linked independent review, both preserved rendering and recovered byte file, and the one-terminal-LF transformation with the recorded 1,454-byte length. Both representations are copied. The resulting hash-matched request checkpoint is distinct from the unavailable final API SQL/digest. C-U093's workflow SQLite/native SQL remain unavailable despite historical hashes; its API-state supplement is correctly identified as a different database. C-U091 retains its pretty-printer limitation, and C-U089 retains its unverified original terminal-newline limitation. Uncaptured locks, journals and post-execution resource inventories are not fabricated.

## Provenance filtering and unchanged paths

Only the exact pinned historical API-digest paragraph is included for these applications. C-U093 additionally receives its pinned workflow-checkpoint paragraphs. The extraction ends before the separate grader discussion. The full outage report, global supplement manifest, other grades and experimental configuration mappings are not copied. The selected source entries belong only to the current application. Original relays and existing embedded paths still provide the protocol's acknowledged provenance hints; this is limited procedural blinding, not perfect anonymization. Review references appear only as paths/hashes, with no permission to follow them outside the assigned packet.

For recovered creators, the intended attachment filtering is otherwise appropriate: it includes only the selected entry, selected placement records, that creator's relay and new format observation. It does not copy the full companion, other creators, consumer-assignment bodies or review/grade bodies. The companion's reviewed hash and all linked records passed real and disposable preflight. Its four format observations report the specified pinned validator, current timestamps, exit 0 and resource hashes matching the new freezes, while explicitly preserving the missing historical reports/freezes/preparation. F1/F2 block this creator path because unreviewed canonical evidence can bypass that filtered attachment.

Non-recovered creators return from `plan_creator` without requiring a companion. Ordinary applications retain their required answer/note/prompt and, for ordinary S06, both initial and final snapshot checks. The fixed supplemental-ID test does not include C-U094–096. Their previously approved recovery-aware identity validation and binding copy remain in the normal S06 path. The new change does not alter `recovery_ledger_binding.py`, `control_ledger_state.py`, the common `BOUNDARIES` string, or `checkpoint.py` at the identities below.

## Verification actually performed

The command `python3 -B -m unittest test_recovered_control_grading test_recovery_ledger_binding -v` exited 0 with **30 tests passed**: 19 supplemental/creator packaging tests and 11 previously approved binding tests. The tests copy evidence to temporary directories and operate only on those fixtures. Their native-state checks and test quota update are disposable infrastructure checks, not business API calls or applications.

The suite covers all ten application output layouts, all four creator attachments, exact copied hashes/modes, source and manifest tampering, missing renderings, original-versus-recovered selection, changed prepared resources, invented originals/final metadata, unknown or noncompleted identities, source symlinks, noncanonical/existing/partial destinations, source changes after preflight, C092's byte proof, filtering, creator companion/review/assignment requirements, changed frozen resources/modes, and the prior restoration/snapshot invariants. Passing these tests does not negate the independent F1/F2 counterexamples.

Six additional independent behavioral checks used only disposable fixtures:

| Check | Result |
|---|---|
| Changed C071 canonical public note | **Defect reproduced:** plan accepted; changed note copied with pinned recovery attachment. |
| Unknown C071 root deliverable | **Defect reproduced:** plan accepted; synthetic unreviewed file copied. |
| Baseline versus current ordinary S06 application-copy loop on identical disposable files, with supplementation disabled | All **12 output files** matched in bytes and modes. This tests copy-loop parity, not full-constructor eligibility for the fixture. |
| Actual current S06 application-copy loop for a disposable restored C094 after deleting its disposable live database | Original and restored paths preserved; copied binding digest equals final metadata; no live database required. |
| Tampered C093 historical workflow-checkpoint paragraph | Rejected with `Historical workflow-checkpoint observation changed`. |
| An unexpected restoration-binding file for completed C086 | Rejected with `A completed supplemental consumer must not have a restored initial-state binding`. |

The integration checks selected and executed the relevant unchanged AST loop from the actual grading helper. They did not invoke the real packet constructor or bypass a gate for a real task. The offline restored-copy fixture used a separately labelled disposable native snapshot and synthetic public observations only. All fixture cleanup completed.

Read-only real preflight then accepted the ten current consumer plans, each containing 14 planned copy sources, and all four current creator attachment plans, each containing two attachment source files. That preflight did not construct a packet and does not resolve F1/F2. The four actual canonical creator-note hashes were independently compared with the unchanged complete relay bodies and all matched. All promised implementation hashes still matched after these checks.

## Reviewed identities

| File | SHA-256 |
|---|---|
| `recovered_control_grading.py` | `d689b33d13602af781371d672eb3ac73fd231d5aab8443c8633e02a26c26b4d8` |
| `prepare_control_grading.py` | `b2a53518d7856819f304ab3dc5e9ec07523efcbc87e143c6cc962e58c93e2aec` |
| `test_recovered_control_grading.py` | `478d538307b849746a4bfb649e1902ff335e8df01fef6d5d46b1d8330dc05f81` |
| Unchanged `recovery_ledger_binding.py` | `3a762fb2dcc9d8c5bf9a7288cef5bb672ad2e2b0c653eaaa04579bfb8477fc9b` |
| Unchanged `control_ledger_state.py` | `86a925979d855b6c11d8297c37663b088331571d6a7317863664b7b17cea4914` |
| Unchanged `test_recovery_ledger_binding.py` | `51747c34d5d93aa25847f07e62a93c261963ab4de9f6ec4b13340bc574de0aef` |
| Unchanged `checkpoint.py` | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |
| `recovery/consumer-evidence/provenance.json` | `4a24e1cb17327ea2b05e11b9c8cabcd2324e6b0ec6f9a8f66bbadadd322bf35b` |
| `recovery/creator-recovery-freezes-001.json` | `03cd21ec820654b6978ea75c903bde1863b1cc625614fe5bbf1859d693f1d402` |
| `recovery/C-U092-request-hash-match-provenance.json` | `1d97138dabefb9389245c0804044cb8733668e75fccd3197328b14917729ee86` |

## Exact approved and blocked scope

Approved after preserving this review and a verified implementation checkpoint: the closed C-U084–093 supplemental application path, within its original fixed preallocated packets once every normal packet-level completion and identity gate is met. Existing or partial packets remain protected from replacement. The unchanged ordinary paths and previously approved C-U094–096 restored-identity/snapshot-copy integration may continue within their existing authorization and verified evidence prerequisites. No actual C094–096 state was operated by this reviewer; any newly completed-context notifications or final-state captures remain coordinator observations.

Blocked at these implementation identities: construction of packets containing recovered creators control-069–072, until a narrow source-note/inventory correction and independent follow-up resolve F1/F2. Retain this failing review and the original implementation identities. Do not work around the block by dropping creator notes, omitting unknown files silently, disabling recovery attachments, copying unreviewed evidence, or changing the pinned companion to accept a different authored version.

Outside this approval: re-authoring or repairing generated Skills; replaying completed consumers; fabricating historical final state, final inventories, missing metadata or grades; new recovery IDs/evidence admitted by relaxing pins; altering criteria, denominators or selection rules; a fourth improvement round; reserve expansion; release judgments or publication. The four remaining reserve starts and first-valid-attempt rules are unchanged. The next step is the bounded implementation correction and follow-up review, not another business trial.
