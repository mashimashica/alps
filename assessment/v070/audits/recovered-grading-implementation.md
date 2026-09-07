# Recovered grading evidence implementation

The supplemental packaging change is ready for independent review. It changes `prepare_control_grading.py` and adds `recovered_control_grading.py` with disposable tests. No real grading packet, business execution, original trial-file edit, new final-state capture, ledger change or Git update was performed by this implementation task.

The inputs are the independently reviewed consumer recovery manifest, the coordinator's separately preserved C-U092 request-byte proof, and the four explicitly labelled creator recovery freezes. Their exact hashes are pinned below and in the helper. Ordinary grading criteria, allocation, schedules, denominators and missing-observation rules remain unchanged.

## Consumer evidence admission

The exceptional path is fixed to completed original S06 applications C-U084–093. It is selected by those exact IDs, not as a fallback when ordinary evidence fails. Each original assignment is pinned by SHA-256. The existing packet constructor still requires completed creators and consumers and validates the fixed allocation, schedules, case bank, oracle, frozen package, consumer identity, original prompt and native initial evidence. For the ten named applications, the new helper additionally checks the closed, reviewed 32-file supplement inventory, its manifest identity, relay hashes and Git blob identities, exact extracted line bodies, and committed matching-SQL source hashes/blobs. Missing, modified or unknown supplements stop preparation.

Every retained prompt and prepared resource must match its original assignment bytes and modes. C-U084/C-U085 surviving original answers, public notes and checkpoints have separately pinned original hashes and mode 0644; a mismatch cannot fall back to a relay. Unknown files in those restored consumer folders, unexpected original final snapshots, or a restoration binding for a completed application require reconciliation. The helper neither fills missing original paths nor invents final metadata.

| Packet location | Evidence represented |
| --- | --- |
| `prompt.md` | Original prepared prompt. |
| `prepared-input/`, `prepared-skill/` | Assignment-backed prepared resources; no complete post-execution inventory is claimed. |
| `original-public-observations/`, `original-work-evidence/` | Surviving original C-U084/C-U085 answers, notes and checkpoints. |
| `recovered-public-text/` | C-U086–093 public answer/note extracts from retained successful-operation relays. |
| `recovered-work-evidence/` | The seven available checkpoint renderings, plus C-U092's separately named hash-matched request bytes. |
| `committed-initial-state/`, `setup-observations.json` | Original assignment-anchored initial SQL/metadata and setup observations. |
| `logical-state-supplement/` | Nine committed SQL contents matching historically recorded final digests; these are not reconstructed original final metadata or new final captures. |
| `recovery-provenance/`, `recovery-provenance.json` | This application's unchanged relay, matching committed SQL source where applicable, filtered source entries and exact selected historical digest paragraphs. |
| `evidence-availability.md` | Explicit representation distinctions and surviving gaps. |

No `observed-final-skill/`, `final-input-state/`, final-resource comparison, or original per-trial final metadata is produced for these applications. The added evidence-boundary paragraph appears only in packets containing these S06 supplements. Existing common grading guidance and the original evidence-boundaries text are unchanged.

C-U091's checkpoint remains labelled a pretty-printed logical rendering; C-U089's display newline remains unverified as an original newline. C-U092's additional request file is checked against the separately pinned proof: exactly one terminal display LF is removed from the preserved rendering, yielding 1,454 bytes with SHA-256 `cf3b8effece5f3c1c9be5e405b5240a66d68d83c984a9795304481974fc486ee`. Both rendering and exact-byte supplement are retained. Its final API SQL/digest remain unavailable. C-U093's workflow SQLite/native SQL remain unavailable; its API-state supplement is a different database.

The full outage report is not copied because it contains other grades and experimental progress/configuration. Only the exact historical API-digest paragraph, and for C-U093 its separate workflow-checkpoint paragraphs, are included. Their SHA-256 values are fixed; a changed paragraph cannot silently become new source evidence. No global consumer provenance manifest, schedule, configuration mapping, other grade or review body enters an application packet.

## Creator recovery freezes

For control-069–072 only, the packet constructor requires the coordinator's exact `recovery/creator-recovery-freezes-001.json`. It verifies its linked reviews, rematerialization and display-recovery observation, then the selected creator's relay, format observation, canonical recovery-freeze manifest, frozen resources/modes and both reconstructed consumer assignments. Normal original freeze/package and application checks remain in the constructor.

Each candidate receives a separate `recovery-provenance/` directory with only its own unchanged authored-text relay, its new format observation, filtered recovery provenance and a plain explanation of the missing historical evidence. The companion's other creator entries, actual consumer-assignment bodies, model/effort mappings, schedules and review/grade bodies are not supplied. The selected creator's rematerialization entries are included where applicable. The evaluated Skill and preserved creator note are not modified.

The current canonical freezes/preparation are described as new recovery observations. Missing original coordinator format reports, freeze manifests and preparation bytes are not claimed recovered. Non-recovered creators do not require this companion or receive the attachment.

## Checks actually performed

`python3 -B -m unittest test_recovered_control_grading test_recovery_ledger_binding -v` passed all **30 tests**: 19 new packaging tests and all 11 previously approved restoration-binding tests.

The new tests create temporary copies and verify complete copy output for all ten application evidence plans and all four creator attachments. They check exact hashes/modes, prepared/original/recovered locations, missing-state distinctions, filtered provenance, C-U092's exact byte transformation and absence of a final API supplement, and unchanged source evidence. Negative cases cover missing/changed/extra supplements, a modified manifest, altered relay or matching-SQL source, a surviving-original mismatch, changed prepared-resource mode/content, invented original final metadata/answer, another or noncompleted consumer, symlinks, noncanonical output paths, changed source after preflight, missing creator reviews/assignments, and changed frozen resource content/mode. Existing or interrupted destinations are retained and rejected for replacement.

One test executes the actual application-copy loop selected from `prepare_control_grading.main`'s AST against a disposable recovered application. It confirms that the integrated path records the original consumer identity once, copies the recovered answer, and does not enter the normal final-resource copy branch. This is execution of the unchanged selected source loop, not a complete real grading-packet invocation.

An additional disposable comparison executed the baseline and changed ordinary application-copy loops against identical surviving files, with the recovery branch disabled. All **nine copied files** matched in bytes and modes. The baseline and current common `BOUNDARIES` strings were identical. This supports preservation of the ordinary copy path; it is not a full end-to-end test of every existing family.

Read-only real-evidence preflight accepted all ten fixed consumer plans and all four exact creator recovery-freeze attachments. No packets were written by that preflight. `python3 -B checkpoint.py verify` passed. Whitespace checks for the new helper/tests and the grading diff emitted no diagnostics; `git diff --no-index --check` returned 1 for differing contents.

## File identities

| File | SHA-256 |
| --- | --- |
| `recovered_control_grading.py` | `d689b33d13602af781371d672eb3ac73fd231d5aab8443c8633e02a26c26b4d8` |
| `prepare_control_grading.py` | `b2a53518d7856819f304ab3dc5e9ec07523efcbc87e143c6cc962e58c93e2aec` |
| `test_recovered_control_grading.py` | `478d538307b849746a4bfb649e1902ff335e8df01fef6d5d46b1d8330dc05f81` |
| Unchanged `recovery_ledger_binding.py` | `3a762fb2dcc9d8c5bf9a7288cef5bb672ad2e2b0c653eaaa04579bfb8477fc9b` |
| Unchanged `control_ledger_state.py` | `86a925979d855b6c11d8297c37663b088331571d6a7317863664b7b17cea4914` |
| Unchanged `test_recovery_ledger_binding.py` | `51747c34d5d93aa25847f07e62a93c261963ab4de9f6ec4b13340bc574de0aef` |
| Unchanged `checkpoint.py` | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |
| Consumer provenance manifest | `4a24e1cb17327ea2b05e11b9c8cabcd2324e6b0ec6f9a8f66bbadadd322bf35b` |
| Creator recovery-freeze companion | `03cd21ec820654b6978ea75c903bde1863b1cc625614fe5bbf1859d693f1d402` |
| C-U092 request-byte provenance | `1d97138dabefb9389245c0804044cb8733668e75fccd3197328b14917729ee86` |

## Limits and next step

Independent review and a verified checkpoint are required before this implementation is used for real packet construction. No complete real S06/S10 grading packet was generated, no business outcome was adjudicated, and no missing original state/inventory was recreated. The reviewed native restored-path behavior remains in place for C-U094–096; those applications still use the normal completed-observation and final-snapshot gates, with both original and restored identities.

The implementation is closed to these particular evidence sets. New recovery evidence or another environment loss requires explicit reconciliation; it is not automatically accepted by changing a local manifest or selecting a fallback. This change does not alter candidate progression, reserve starts, denominator accounting, example eligibility or release authority.
