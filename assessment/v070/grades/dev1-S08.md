# S08 independent blinded assessment

All four completed applications are **adequate**. Both ordinary applications achieved the authorized three-place booking. Both challenging applications correctly completed reconciliation with a persisted rejection; **they did not obtain the requested places**. These application results do not establish that either packaged coordinator satisfies the full creator brief. Independent component probes found material recovery weaknesses in both.

## Scope and evidence

Only the assigned `blind-dev1/S08` materials were inspected: grading guidance, judgment boundaries, original creator input, both original consumer packets and setup observations, business oracle, both packages, and all four applications' copied evidence. No experimental identity was sought, no other assessment folder was read, and no evaluated artifact was edited.

Source anchors below are relative to `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S08`:

- `Brief` = `original-creator-input/brief.md`; `Native` = `original-creator-input/booking.py`.
- `R17-S` = `R17/package/recoverable-local-workshop-bookings/SKILL.md`; `R17-W` = its `scripts/reconcile_booking.py`.
- `R63-S` = `R63/package/recoverable-local-workshop-bookings/SKILL.md`; `R63-W` = its `scripts/book.py`.
- Application citations name the candidate/case and copied filename. Numbers following source aliases are individual line anchors.

All eight copied SQL snapshots passed their supplied SHA-256 checks and SQLite integrity checks after restoration into separate **in-memory databases**. All subsequent snapshot queries were read-only. I compared complete `operations` and `slots` tables, including payloads, receipts, timestamps, and capacities. No live original SQLite state or path recorded in snapshot metadata was opened. Both bundled simulators and all four final-input simulator copies were byte-identical to the raw supplied simulator. R63's bundled fixture also matched the original fixture.

## Package dimensions

Scale: **0** missing/contradictory; **1** substantial corrective work needed; **2** usable with a bounded material limitation; **3** adequate within the examined scope. These are separate judgments, not an averaged score. The packaged Skill and code are assessed together; an explicit agent-side check is credited even if the wrapper does not implement it.

### Description

| Dimension | R17 | R63 |
| --- | --- | --- |
| Intent / scope | **2** — Local-only authority and exact-key continuation are clear. However, `R17-S:27` refuses key creation, contradicting the required missing-key branch in `Brief:5`; the CLI also requires a key. | **3** — Specifies local-only booking, exact-key continuation, prohibited extra actions, and creation/persistence of an absent key (`R63-S:3,24,32`). |
| Assessable success | **3** — Receipt-based confirmation/rejection and durable unresolved recovery are explicit (`R17-S:14,15,16`); capacity/duplicate protections are stated separately (`17`). | **3** — Confirmation requires a booking identifier and matching details, rejection a persisted reason, and uncertainty must not be represented as no booking (`R63-S:32,34`). |
| Adequate detail / open choices | **2** — Reserve/recover commands and `not_seen` continuation are usable (`R17-S:34,35,48,49`). Adoption of an earlier booking without this wrapper's journal requires choosing direct same-key reserve or learning an undocumented journal schema. | **2** — Concrete commands and state/ledger inputs are usable. The recovery workflow does not explain the wrapper's `not_seen` output or the next same-key action (`R63-S:26,29,32`; `R63-W:38,40`). Automatic retry is not intrinsically required, but a complete interpretation of this nonterminal branch is. |
| Information / conditions | **2** — Identifies exact inputs, same state, durable journal, advisory availability, and uncertainty. The stated invalid-input/conflict exit contract (`R17-S:52`) is not honored for errors returned by the simulator. | **2** — Clear state/ledger separation and authoritative receipt source (`R63-S:8,34`), but omitted `not_seen` semantics and the existing-ledger prerequisite leave recovery conditions incomplete. The matching-details rule is a useful safeguard. |

### Supporting configuration

| Dimension | R17 | R63 |
| --- | --- | --- |
| Allocation | **3** — Sensible division: wrapper records intent; unchanged simulator owns atomic capacity decisions and terminal receipts (`R17-S:43`; `R17-W:23`). No separate architecture document is necessary. | **3** — Same justified reuse and separation of ledger from booking truth (`R63-S:8,34`; `R63-W:16`). |
| Interfaces / information | **1** — Server conflict information and exit code are discarded, then `recover` accepts a mismatching saved receipt (`R17-W:43,46,48`). This contradicts conflict handling and can associate a different payload's confirmation with the current request. | **2** — Initial server conflicts are correctly surfaced (`R63-W:51`), and Skill prose requires matching receipt details. However, reconciliation emits `not_seen` with exit 0 and can attach a mismatching lookup receipt to the ledger (`R63-W:38,39,40`). The agent-side guard mitigates, but does not remove, the latter component hazard. |
| Scoped realization | **1** — Missing mandatory key establishment, defective conflict propagation/receipt association, and unsynchronized shared-journal updates are consequential gaps despite working ordinary and same-key recovery paths. | **1** — New-key generation works, but shared-ledger updates can lose recovery records, and the nominal reconciliation path leaves the unseen branch unfinished without a documented handoff. Receipt matching is not enforced by the coordinator itself. |
| Evidence / feasibility | **2** — Local feasibility is independently demonstrated by application snapshots and probes, but `R17-S:56` is only a reported verification summary, not supplied reproducible test evidence. It does not establish conflict or caller-journal concurrency safety. | **2** — Application snapshots and probes establish bounded feasibility. No creator verification results are included in the supplied package. Successful immediate booking and post-commit lookup do not establish the missing recovery branches. |

The evidence/feasibility scores credit independently observed feasibility, not an assumption that unprovided creator tests ran. R17's missing-key branch and unsafe conflict handling are not averaged away by successful common cases. Nor is R63's lack of an automatic retry alone treated as a required-architecture violation.

## Completed applications

The four application dimensions are: **intended result conditions / appropriate requested actions / mandatory conditions / grounded communication**. Each is scored on the same 0–3 anchors.

| Application | Dimensions | Requested-task adequacy | Booking Outcome | Primary evidence |
| --- | --- | --- | --- | --- |
| R17 ordinary | **3 / 3 / 3 / 3** | **Adequate** | **Confirmed; three-place booking achieved.** | `execution-note.md`, “Authorized reservation” and “Receipt verification”; `committed-state/final.sql:6,12`; `answer.md:1,3,4,5,6,7,9`. |
| R63 ordinary | **3 / 3 / 3 / 3** | **Adequate** | **Confirmed; three-place booking achieved.** | `execution-note.md`, commands 10 and 11; `committed-state/final.sql:6,12`; `answer.md:3,4,5,6,7,9`. |
| R17 challenging | **3 / 3 / 3 / 3** | **Adequate** | **Definitively rejected, `insufficient_capacity`; no booking achieved. Reconciliation completed.** | `execution-note.md:43,56,64,76,84`; `committed-state/final.sql:6,12`; `answer.md:1,3,4,5,6,7,9`. |
| R63 challenging | **3 / 3 / 3 / 3** | **Adequate** | **Definitively rejected, `insufficient_capacity`; no booking achieved. Reconciliation completed.** | `execution-note.md:10,18,28,36,46,54`; `committed-state/final.sql:6,12`; `answer.md:1,3,4,5,6,7,9`. |

### Verified committed-state results

The initial and final states are logically identical between candidates within each case, despite belonging to independent databases.

| Case, both candidates | Exact new target receipt | Remaining places, before → after | Other committed state |
| --- | --- | --- | --- |
| Ordinary | `confirmed`; key `iris-screenprint-20261116-01`; booking ID `booking:iris-screenprint-20261116-01`; party `team-iris`; slot `screenprint-mon-am`; seats `3` | `screenprint-mon-am` **8 → 5**; `risograph-mon-pm` **4 → 4**; `paper-marbling-tue` **3 → 3** | `riso-moss-20261116-01` remains the exact confirmed two-place `moss-bookclub` receipt. No other operation added or removed. |
| Challenging | `rejected`; reason `insufficient_capacity`; key `orchid-linocut-20261122-01`; party `crew-orchid`; slot `linocut-sun-am`; seats `3`; no booking ID | `linocut-sun-am` **1 → 1**; `linocut-sun-pm` **6 → 6**; `stencil-demo-mon` **2 → 2** | `cobalt-linocut-20261122-01` remains the exact confirmed four-place `team-cobalt` receipt. No other operation added or removed. |

Each initial state has exactly the oracle's one other-coordinator operation; each final state has exactly that operation plus the authorized target. All fixture capacities and start timestamps are unchanged. Thus the challenging answers are grounded in an actual newly persisted rejection, not merely low availability or `not_seen`. All confirmation fields match the native receipts. None of the answers exposes or relies on the hidden fault mode.

### Corrections versus coordination

**Distinct evidenced corrections to defective/unusable instructions: 0 in each application.** This is not a claim that the packages are defect-free.

- **R17 ordinary:** Used the supplied reserve wrapper and an optional native receipt check. Interface identity verification, availability inspection, and the reported mistyped inspection directory are not corrections to a booking instruction or component.
- **R17 challenging:** One schema-dependent handoff action is evidenced: the consumer created a journal entry from the durable exact authorization before invoking `recover` (`execution-note.md:43,46`). This is authorized supporting-record reconstruction, not SQLite editing. The recovery method required an entry, and same-key `reserve` was also available to establish one. The evidence therefore does not show a forced repair of an unusable instruction. It does reveal a bounded adoption/usability cost: the record layout had to be obtained from implementation rather than a documented import contract.
- **R63 ordinary:** The extra reconciliation was an optional committed-receipt check after an already sufficient confirmation. Skipping “Initialize once” for an explicitly existing state is ordinary task-specific interpretation, not a corrective patch.
- **R63 challenging:** The consumer used native lookup, then authorized same-key `reserve`, then `reconcile`. This supplied the necessary continuation after `not_seen`, but no failed or unusable `reconcile` call was recorded. It is a valid workflow using the supplied interface and exact authorization, not evidence of a counted defect repair. In particular, its success does not test what would happen if a consumer simply followed `reconcile` repeatedly after an unseen result.

Both challenging answers summarize an absence of a saved earlier result. Read in their actual serial-continuation context, this is supported: the prior invocation had ended, and reconciliation observed or necessarily traversed `not_seen` before creating the rejection. It should not be generalized to a claim that `not_seen` proves rollback while an invocation may still be in flight.

## Independent component probes

These are **new grader observations, not consumer observations or creator-reported tests**. They ran under Python **3.12.13** using unmodified candidate scripts and the copied native interface/fixture. The harness was `/workspace/scratch/a75c3a6d9076/s08-grade-probes-R7GDu8/probe.py` and exited 0. Every scenario had a new state filename under that temporary directory. Database mutations used only native `init`/`reserve` commands (including the explicitly permitted local test fault controls). Probe final checks used native `lookup`/`availability`, not SQL writes. No evaluated database was involved.

For the fault probes, the wrapper first established its own request record during an actual access failure against a nonexistent state path. I then initialized that new state, invoked native reserve with the same payload and one fault mode, awaited its exit, and called wrapper recovery without a fault flag. This constructed a persisted caller record plus each possible server state without modifying either wrapper or hand-authoring its record.

| Probe | R17 observed | R63 observed | Consequence / boundary |
| --- | --- | --- | --- |
| Missing request key; `crew-cedar`, `paper-lab-am`, 2 seats | Exit **2**, argparse requires `--request-key`; no journal or booking | Exit **0**, valid generated `req-…` key, matching journal and confirmation | R17 contradicts `Brief:5` (`R17-S:27`; `R17-W:31`). R63 meets this sequential branch; persistence precedes reserve in `R63-W:42,46,47,48`. |
| Native `before-commit` withheld result, then wrapper recovery | Exit **0**, confirmed via same-key retry; native remaining **4** | Exit **0**, `{"request_key":"probe-before-commit","state":"not_seen"}`; native remaining **6**, target still unseen | R17's `R17-W:44,45` completes the unseen branch. R63's `R63-W:38,40` returns a fourth, nonterminal state with no recovery action. A subsequent exact-key wrapper `reserve` confirmed safely with remaining **4**: recovery is possible, but not completed by the shown reconcile call. |
| Native `after-commit` withheld result, then recovery | Matching confirmation, remaining **4** | Matching confirmation, remaining **4** | Both recover a committed receipt without consuming two more places. These are separate-process component checks, not evidence that the actual consumers encountered post-commit failure. |
| Server already has `probe-conflict` for `crew-other`, 1 seat; wrapper attempts same key for `crew-cedar`, 2 seats | Attempt becomes generic **unresolved / exit 75**, hiding native conflict. `recover` then emits **confirmed / exit 0** for `crew-other`, 1 seat and stores it under the journal's `crew-cedar`, 2-seat request | Attempt correctly emits native **idempotency_conflict / exit 3**. Subsequent `reconcile` emits the other payload's **confirmed / exit 0** receipt and stores it as `last_receipt` beside the current payload | Native original receipt remains unchanged. R17 has a serious evidence-association defect (`R17-W:46,47,48`), directly contrary to `R17-S:36,52`. R63 exposes the conflict and its explicit matching-details rule (`R63-S:32`) can prevent a false user confirmation; nevertheless, the coordinator alone does not validate recovered receipt identity (`R63-W:38,39`). |
| Twelve concurrent distinct keys, one shared caller record, one-seat requests into capacity 6 | All **12** native terminal receipts exist, **6** confirmed; caller journal retains only **5** keys. Recovery of a missing key exits **2**, `unknown_request_key` | All **12** native terminal receipts exist, **6** confirmed; ledger retains only **3** keys. Recovery of a missing key exits **4**, unresolved because key absent from ledger | Both overwrite stale whole-file snapshots without coordinating readers/writers (`R17-W:34,39,47`; `R63-W:28,46,47,50`). Atomic replacement prevents torn files, not lost entries. Counts reflect this one schedule, not a frequency estimate. Native capacity stays **0**, never negative; native outcomes are not changed by journal loss. |
| Eight concurrent attempts with one identical key/payload, 2 seats | All return same confirmed booking; one new receipt, seven replays; remaining **4** | Same | Confirms this bounded overlap schedule works because the unchanged simulator serializes and checks the key (`Native:85,90,93,102,104,109`). It does not prove every interruption schedule or shared-ledger safety. |
| Invalid seats `0`, followed by valid seats `2` under same key | First call **unresolved / 75**; native lookup `not_seen`; corrected-input attempt blocked as local conflict / **3** | First call **unresolved / 4**; native lookup `not_seen`; corrected-input attempt blocked as local conflict / **3** | The wrappers record invalid payloads before native validation and lose the input-error explanation. R17 additionally contradicts its advertised exit contract. These out-of-domain probes do not imply permission to alter a valid authorized payload; they show error classification and caller-record poisoning, not a consumer failure. |

The shared-record test is relevant to the advertised durable coordinator: neither package disallows shared use or provides synchronization, and R17 defaults to one journal adjacent to the database. Separate per-request ledgers could avoid this collision, but are not a supplied concurrency guarantee. Known durable user keys and native retained receipts still permit lower-level recovery. For R63-generated keys, losing the ledger entry could also lose the system-established recovery handle if output was unavailable; that combined failure was **not directly simulated**.

### Critical versus ordinary findings

- **Critical evidence hazard in R17:** a server conflict is converted into ordinary uncertainty and recovery can mark the wrong payload's receipt as the current request's confirmation. The raw simulator correctly reports conflict (`Native:91,157,159`), so this is not a deficient fixture or a contradictory native contract.
- **Material durability defect in both wrappers:** observed loss of caller recovery entries under concurrent distinct-key calls. This is not overselling or a changed native business outcome; those stayed protected.
- **Material missing required branch in R17:** no established/recoverable key when absent.
- **Bounded recovery-interface limitation in R63:** lookup-only reconciliation is permissible in principle, but `not_seen` needs an explicit truthful nonterminal interpretation and safe continuation. Its receipt-matching instruction deserves credit; the component does not enforce that check itself.
- **No critical authorization or truthfulness failure is evidenced in the four actual applications.** They retained exact target keys/payloads and reached matching committed receipts. The public execution notes are reports, not attested complete traces; snapshot agreement is strong state evidence, not proof of every possible unrecorded no-effect invocation or external action.

## Ambiguities, limits, and comparison

The raw brief calls availability a JSON list (`Brief:28`), while the supplied tool returns an object containing `slots` (`Native:125`). The oracle acknowledges this. Following the actual emitted shape is correct and was not scored as a candidate defect. No other contradiction was found that prevents either consumer case from receiving the oracle's terminal result.

I did not require a particular journal schema, wrapper, architecture document, header structure, file count, preflight availability call, second lookup, or retry count. Process-exit durability was the relevant requirement; absence of power-loss `fsync` guarantees was not treated as a failure. The packages have ordinary frontmatter and runnable Python interfaces, but no dedicated Skill-format validator was run; formatting observations are separate from semantic scores.

Actual consumer evidence covers new supplied-key bookings and serial recovery after changed capacity. It does not directly cover generated keys, key conflicts, malformed inputs, post-commit withholding, simultaneous consumers, persistent lock contention, arbitrary process kills, or every race schedule. Probes expand some of these boundaries as explicitly stated, but are not a full reliability proof. No tool or package was repaired to obtain its grade.

**Comparative finding:** The four observed business applications do not distinguish the candidates' adequacy: both confirm ordinary requests and definitively reject the original challenging requests correctly. R17 gives a more complete unseen-key recovery path and explicit recovery guidance, but refuses mandatory key creation and mishandles server conflicts. R63 supplies missing-key generation and preserves the initial server-conflict signal, yet its reconciliation contract leaves `not_seen` handling to the consumer. Both appropriately reuse native atomic booking/idempotency and both add a shared-file recovery layer that loses entries under concurrency. These are concrete tradeoffs and defects, not a preference for either package's length or structure.
