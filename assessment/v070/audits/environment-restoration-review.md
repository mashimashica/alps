# Independent environment restoration review

Verification scope: read-only inspection of the immutable evidence checkout at commit `75c0ea9bddf379c5e1803e4c0114ba5b47c871d8`, under `/workspace/scratch/a75c3a6d9076/alps-evidence-recovery-75c0ea9/assessment/v070`, plus in-memory SQL restoration checks. No original business database or trial file was changed. The completed report follows unchanged; a coordinator-requested continuation recommendation is appended separately.

Recovery can continue without new business trials, but the current helpers do not support every required recovery case. The immediate blocker is explicit binding of restored S06 databases at new paths. Missing evidence from completed work must remain separate from application validity.

I performed only read-only evidence inspection and in-memory SQL checks. No files, original databases, business operations or trials were changed.

| Evidence checked | Finding |
|---|---|
| Approved helpers and fixed identities | Helper hashes, both schedules, case manifest and grading allocation match the declared identities. |
| S06 state evidence | All 24 initial observations, C-U073–096, and 11 saved finals, C-U073–083, have valid hashes and matching consumer/path bindings. All 35 dumps restore in memory, pass `quick_check`, and reproduce their exact dump under SQLite 3.53.1. |
| C-U094–097 | Original prompt hashes, copied resource hashes and modes match. |
| Indexed SQLite evidence | All 24 entries have valid SQL and metadata hashes. |
| C069/C070 | Their four original files each exactly match the final relayed text, including terminal newline. |
| C-U084/C-U085 | Both original answers and notes match the final relays. C-U084’s checkpoint also matches. C-U085’s original checkpoint is committed: 969 bytes, SHA-256 `29a3cd1b8aab2b3b35548c14fad40f473472683e84bd1f8343984080b7cfb173`, matching the historical size observation. |
| Remaining original artifacts | C071/C072 authored files, all four later freeze manifests and physical-format reports, and C-U086–093 final files are absent from their original locations. |

The permitted recovery boundaries are:

- **Completed creators001–072 and consumers001–093:** preserve completion. Extracting retained successful patches or captured outputs is evidence recovery, not another execution. Do not rerun these tasks. Grade surviving evidence normally; use “unconfirmed” only where a required observation remains unsupported. Missing raw state does not automatically invalidate an otherwise supported application.
- **C-U094–097:** retain their existing contexts and original attempt IDs. Their recorded failures occurred before reading task resources or operating on state. Restoring the prescribed initial logical state for C-U094–096, then resuming those contexts, does not consume a retry. C-U097 requires no S06 database restoration.
- **C-U098–136:** their saved preparation can support their first scheduled starts after integrity verification and the recovery checkpoint.
- **C-U137–144:** rebuilding lost preparation is bookkeeping, not a new task. However, the source-package and freeze evidence must first be reconciled as described below.
- **Distinct retry:** necessary only if a pending original context or required attempt state proves unrecoverable and independent arm-blind infrastructure adjudication permits replacement. Retain the original, assign a distinct `-R1` identity, allow at most one retry, and select the first valid attempt. The H02 retry helper is hardcoded to two H02 IDs and must not be reused for C. Four reserve starts remain; they do not authorize a fourth improvement round.

The smallest valid procedure is:

1. Preserve the verified evidence snapshot and older filesystem separately. Restore the evidence root at its recorded location, preserving emergency recovery files and original metadata. Reconcile ledger statuses from explicit notifications using `record_status.py`, without replacing existing timestamps or inventing missing historical times. For completion reconciliation, `--status completed` without `--event` avoids creating a false historical completion time; record the recovery observation separately.

2. Recover committed and relayed content with explicit provenance. Keep the relays unchanged. Label extracted files as transcript-derived where no original bytes survive. C069/C070 have direct committed-byte corroboration; C071/C072 currently do not. Do not fabricate their missing original freeze inventories, file modes or validator reports.

   A fresh mechanical format check and a newly timestamped recovery freeze are permissible infrastructure observations, but cannot be described as the lost original checks/freezes. Before preparing C-U137–144, independently review whether the recovered package evidence identifies the complete final authored version sufficiently. If C071/C072 cannot be established, retain their completion and block only their dependent consumer slots; do not commission new authoring under the old IDs.

3. Restore only the state needed for pending work. For C-U094–096, use their assignment-anchored `initial.sql`, create exclusive new database files in new allocated directories, and verify:

   - Source SQL and metadata hashes, original setup identity and original path.
   - Successful SQL restoration, `PRAGMA quick_check`, and exact dump equality.
   - Unchanged prescribed snapshot, records, tranche and unused quota.
   - A recovery record containing original path, new path, source evidence hashes, restored logical-state hash, current binary hash and observation time.

   Do not invoke `init`, `page` or `grant-tranche`. Do not restore a completed consumer’s initial state and call it its final endpoint.

4. Add and independently review narrow recovery-binding support before resuming C-U094–096. **There is no safe existing rebind CLI.** `control_ledger_state.py` reads the original immutable setup path; `prepare_control_grading.py` requires final metadata to use that same path. `RESUME.md` explicitly requires lost SQLite restoration to a **new path**.

   Preserve setup, prompt, request, initial SQL and original hashes. A separate recovery binding must connect the original assignment to the new database. A minimal continuation message may override only the obsolete state-path literal for the retained consumer context. Snapshotting and grading must retain both original and restored paths rather than falsifying the original setup record.

5. Preserve remaining evidence gaps explicitly:

   - The historical final-SQL hashes for C-U084–091 and C-U093 match committed SQL elsewhere. Those bytes may be preserved as a **content-addressed recovery supplement**, citing both the historical digest observation and the actual source blob/path. This recovers matching logical content; it does not recover original per-trial metadata or constitute a fresh final-state capture.
   - C-U092 has no captured final API hash or SQL. Leave that observation unavailable.
   - No committed SQL matches C-U093’s workflow-checkpoint hash `2f30def62fff9a87c9ebfa3d82235d7c627cb6df9d489a376f35396f4538c87c`. Do not synthesize it.
   - C-U091’s pretty-printed JSON preserves logical content, not original compact bytes. Missing locks and journals remain missing.
   - The S06-P02 report and probe relay survive. Missing original probe databases and JSON serialization remain gaps. Required independent review can perform separately labelled disposable component checks; those do not recreate the original observations or add consumer trials.

6. Save the reconciled evidence and explicit gaps before new work. Rebuild the publication cache only against the verified remote tree; `checkpoint.py mark` fingerprints local files and does not itself verify remote preservation. Run `python3 -B checkpoint.py verify`, validate representation hashes, and perform the existing exact-ref direct-API checkpoint with read-back verification. Resume the retained contexts, then unaffected scheduled consumers.

Normal blind packaging currently blocks on missing original final files/state and cannot honestly absorb transcript reconstructions by filling its expected filenames with invented metadata. A narrowly reviewed supplemental-evidence packaging path must preserve these distinctions. Independent graders can then apply the unchanged criteria and missingness rules.

The observed completion count remains 267, including 165 C tasks. Recovery adds none. Fifty-one scheduled C applications remain; the separate 1,776 candidate-dependent slots and the three-round cap remain unchanged.

## Continuation recommendation after the coordinator’s restoration update

The coordinator reports that all 5,290 tracked evidence files now match their exact Git blob SHAs and modes at the original assessment root, frozen hashes and approved helper digests pass, the older H02 filesystem is preserved separately, and the publication cache was rebuilt only after exact restoration. These are coordinator observations; I did not repeat them or inspect the restored working tree for this addendum.

After ledger reconciliation and the verified restoration checkpoint, I recommend resuming **the retained C-U097 context** with its original prompt and S09 inputs. Its prompt, resource hashes and modes passed this review, and it needs no S06 API database. This is continuation of its existing attempt and consumes no reserve start.

I also recommend starting the never-started **C-U098–120 S09 consumers** in their scheduled fresh gpt-5.6-sol/high contexts, using the saved prepared packets and fixed assignment order. They are first starts in existing base slots, not retries. Record their actual start observations normally. The outstanding S06 restoration-binding support is not a dependency of these static S09 tasks and should be addressed independently. Preserve missing S06 native-state evidence and its limitations; do not fabricate historical final captures to permit S09 progress.

Keep C-U094–096 paused in their retained contexts until the separate bounded recovery-binding review passes and the resulting recovery evidence is saved. This recommendation does not authorize a new candidate round or change any grading, first-valid-attempt, retry, reserve or release boundary.
