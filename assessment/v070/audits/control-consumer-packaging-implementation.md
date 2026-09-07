# C consumer packaging implementation check

The three new helpers below implement experiment packaging and physical-format observations. They do not change ALPS, stage a live consumer, execute a model task, inspect actual generated C Skill content, grade an artifact, or change the blocked-stage decisions. No existing helper, case, oracle, creator assignment, schedule or execution ledger was modified by this subtask. No applicable parent-directory `AGENTS.md` was found for this evidence folder.

| File | Checked SHA-256 | Responsibility |
| --- | --- | --- |
| `prepare_control_consumers.py` | `f6bba138b7c1920c73a70eca7065a435eb9ca2e074648dd52ddbf14177ebc642` | Freeze supplied resources, prepare two fixed consumer copies and record external metadata for explicitly completed creators. |
| `control_ledger_state.py` | `d882ca0323dd6e8887017b74ea1dc7adc06bd8cd1c0b3b92deda00c26932094d` | Initialize the prescribed S06 native state and preserve initial or later read-only native SQL snapshots. |
| `validate_control.py` | `c62f075604e6c11921f8a152f20b68615783296e1a59f0b28162d95c14791d0f` | Run the existing pinned Agent Skills physical-format validator on explicit completed creator IDs; preserve one exclusive observation per creator. |

## Boundaries and identity

Preparation requires distinct explicit `control-NNN` IDs, each marked `completed` in the current coordinator ledger. It verifies all 72 assignment cells against the immutable creator schedule and its known digest, `739210b57f1b000dcb3cf6f4e2ee912ca6e911d8e829eacde225bb03ffe91569`. Every selected creator's external assignment, original input file set and bytes, and supplied prompt hash must match the frozen public source and assignment. One immediate self-contained Skill directory containing `SKILL.md` must exist under that creator's `deliverables/skills/`. A missing or ambiguous artifact causes a concrete packaging refusal, not an automatic quality score.

The complete frozen public case bank is verified against `main-case-hashes.json`. The independently reviewed 29-file consumer bank must exactly match `control-consumer-case-hashes.json`, whose fixed digest is `f26be07f6cfba54aedc3068a67ae32292877f6ee005f0c190156f5786d1cbdc2`. All seven originally recorded skill-creator text-resource hashes are checked. Its two existing display assets, `assets/skill-creator.png` and `assets/skill-creator-small.svg`, are absent from the original 77-resource hash manifest. Their current hashes are recorded in consumer metadata without claiming original hash verification. No other unrecorded aid files are accepted. No ALPS authoring path is supplied to C consumers.

Before the first write, the entire requested batch is checked for existing or partial freezes, consumer folders, external assignments, setup records, snapshots and allocated native-state directories. Existing files, dangling links and unexpected parent entries are preserved and refused. A later write/setup failure leaves its evidence for explicit reconciliation; preparation is not a filesystem transaction and must not be rerun over a partial attempt.

Resource bytes are copied first to `frozen/control-artifacts/<creator-id>/<skill-name>/` and verified against the unchanged original. The external `control-artifact-freezes/<creator-id>.json` records the resource hashes and original file modes. Only regular `.pyc` files directly inside `__pycache__` are omitted as Python runtime caches. Their original paths and hashes are explicitly recorded as excluded; the original files are retained and their bytes are not claimed durably preserved. Any non-cache resource inside that directory causes a pre-write limitation because the existing checkpoint helper omits that directory. Other resources, including arbitrary binary files, are not silently excluded. Binary retention in local packaging does not establish that the UTF-8 Git checkpoint path can save a particular binary resource.

For creator number `n`, ordinary and challenging consumers are fixed as `C-U{2n-1:03}` and `C-U{2n:03}`. Each is assigned a fresh gpt-5.6-sol/high context in external metadata. Both receive copies with identical resource bytes and preserved executable modes. The metadata records the freeze identity, original bank identity, materialized copy hashes, prompt hash, original request hash and every actual path substitution with its occurrence count. Only the existing `{{INPUT_DIR}}`, `{{STATE_PATH}}` and S10 `{{ENVIRONMENT_PATH}}` path placeholders are bound. The reviewed request source is unchanged. The coordinator separately owns the immutable consumer schedule and mutable execution ledger.

The supplied consumer prompt retains the original common optional skill-creator availability, local working directory, no-workspace-enumeration and no-delegation conditions. Supplied Skill and original input changes, external business writes and sending messages are unauthorized. Explicitly authorized simulator effects occur only through the supplied interface. Answers and public execution notes go outside the Skill. An inadequate supplied Skill is reported without repair; independently valid task work may continue. These are procedural access restrictions, not an enforced sandbox.

## State and tool packaging

S06 receives the unchanged frozen `ledger_api.py`. Its hidden fixture is used only by setup, outside the consumer folder. The helper initializes a unique SQLite file in an allocated directory alongside the evidence root, records the exact `init` and unmetered `describe` calls, and verifies snapshot identity, record count, tranche 1 and two remaining page calls. No setup page call or additional tranche is used. Initial native SQL and its hash are saved in `state-snapshots/<consumer-id>/` outside the consumer context. A later explicitly labelled snapshot uses a consistent read-only transaction and records native SQL, SQLite version and hash. It consumes no API page quota. It represents committed logical state and does not claim SQLite byte identity, complete execution history or successful business work.

S10 receives the unchanged frozen `release_tool.py` and its own copied JSON simulation state. Its existing environment-path placeholder resolves to that consumer's input directory. Original static input hashes remain available to `verify_consumer_artifacts.py`; S10 state changes still require behavioral review. S06 state is separately preserved through native SQL and setup metadata. The existing integrity helper remains a check of recorded original resource files and does not prove the absence of added files or prohibited reads.

## Checks actually performed

The exact final public output is retained in `audits/control-consumer-packaging-check-output.json`. The one-off disposable check source remains at `/workspace/scratch/a75c3a6d9076/control-packaging-disposable-check.py`, SHA-256 `fb9ad6522dca5a6ceadf74b60d73c6ca0d7eac604fd5f1834ee5d11c8926fd71`. It is a temporary check harness, not a product test or permanent validation gate.

The final check command, run from the evidence root, was:

```sh
python3 /workspace/scratch/a75c3a6d9076/control-packaging-disposable-check.py
```

It exited 0 and reported 23 passed checks. The harness copied raw public inputs, assignments, reviewed consumer cases, the common aid and helper files into disposable trees. It fabricated six identical synthetic Skills, one for each selected family; it never read actual C Skill bodies or ran a consumer. Each synthetic Skill included an executable script that was not to be executed, a binary resource and a disposable Python cache. The script was not executed. A single S06 page call in a disposable setup checked snapshot preservation; it was an infrastructure check without a model task or business-outcome judgment.

| Check | Observed result |
| --- | --- |
| Six-family successful packaging | Twelve ordinary/challenging copies prepared with the correct fixed IDs, fresh reference configuration, no hidden fixture in inputs and no ALPS authoring path in prompts. |
| Source/freeze/copy resources | Exact resource hashes matched; arbitrary binary resource retained; executable `0755` mode retained. |
| Runtime cache | Original `.pyc` retained, its path/hash recorded as excluded, and no frozen/copied cache byte falsely claimed preserved. |
| Request bindings | Every recorded token/count reconstructed the actual request; no unresolved token remained. |
| S06 initialization | Two distinct native states outside the evidence root; exact setup observations; both began at tranche 1 with two calls available. |
| Native SQL | Initial dumps restored in memory to the original record counts and `(tranche, calls_used) = (1, 0)`; after one disposable page, the later dump restored `(1, 1)` and the snapshot itself did not change the source file hash. |
| Pinned physical format | The synthetic Skill passed the pinned `skills-ref` validator, exit 0. This was not a live C artifact validation. |
| Repeated format report, snapshot and preparation | Each refused without replacing existing evidence. |
| Incomplete, duplicate or unknown creator IDs | Each refused before writes. |
| Changed schedule digest, bank bytes, bank manifest, public API or creator prompt | Each refused before writes. |
| Dangling creator input or owned consumer/assignment/freeze/setup/snapshot destination | Each refused before writes. |
| Non-cache resource in `__pycache__` | Refused before writes; arbitrary resource was not silently excluded. |
| Existing later consumer in a two-creator batch | Refused before creating the first selected creator's freeze or consumer. |
| Orphaned native-state allocation | Refused without allocating a replacement state. |

Python 3.12.13 and SQLite 3.53.1 were observed. The pinned physical validator identifies `agentskills/agentskills@f130f348f502d9804278a617f86929846896d2e9`; this check used the existing runtime dependency installation, not a newly fetched version. A final `ast.parse` pass for all three helpers succeeded without writing bytecode.

Earlier check attempts are not hidden: the first stopped before packaging when the seven-record aid manifest did not include its two display assets; the helper now states and records that limitation. The next stopped because the disposable fault-injection harness tried to alter its own read-only schedule copy; that harness now changes only its disposable copy's permissions before fault injection. A later passing check initially encountered a retained disposable native-state allocation before the intended later-batch partial-folder condition; that case was changed to a stateless family so the final check exercised the intended `C-U026` destination refusal directly. These were infrastructure development observations, not consumer retries or artifact-quality evidence.

## Use after independent review and checkpoint

The coordinator may prepare explicit completed IDs with `python3 -B prepare_control_consumers.py control-001 ...`, run one physical-format observation per explicit ID with `python3 -B validate_control.py control-001 ...`, and preserve completed S06 state with `python3 -B control_ledger_state.py C-U073 --label final`. These are usage examples, not claims that live preparation, validation or final-state collection occurred here. No live consumer folder or model task was created in this subtask. Independent review and durable checkpointing remain the coordinator's next steps.

## Bounded initial-metadata follow-up

After the first independent review was saved, `prepare_control_consumers.py` changed to SHA-256 `4a3cfe4e641d91c90348b19f128b6e281b898414d0ff157538d550f5f51ca32c`. The other two helper hashes above remain unchanged. Consumer metadata now records `copied_file_modes` for exactly the paths in `copied_sha256`, using `stat.S_IMODE`. For S06 it also records `initial_state_evidence_sha256`: assessment-root-relative paths and hashes for the matching setup JSON, `initial.sql` and `initial.json`. This map is empty for the other families. These fields describe initial observations for later provenance checks; they do not alter prompts, resources, state or ledgers.

The reviewer reproduced a resource under `.local/` that the old inventory would accept but the existing checkpoint helper would omit, and confirmed the same static condition for `.git/`. Artifact preflight now explicitly refuses those path components, including the Skill directory name, while preserving the original resource. The existing non-cache `__pycache__` refusal also covers the Skill directory name. This reports a concrete storage limitation; it does not exclude or repair arbitrary resources or assign a Skill quality score.

The bounded command `python3 -B /workspace/scratch/a75c3a6d9076/control-packaging-metadata-check.py` exited 0. Its temporary source SHA-256 is `12650cf0b24a02b8515c299a1ab518f3a0c33029442f5b1b686515930ad05593`; the exact output is retained in `audits/control-consumer-packaging-metadata-check-output.json`. Four disposable consumers from two synthetic Skills were read back: all mode-map keys matched the byte-map keys and actual files; executable `0755` and read-only `0440` modes were recorded correctly. Both S06 metadata files bound exactly three existing initial evidence files to their observed hashes, with two API page calls still available. Separate synthetic `.local/evidence.txt` and `.git/evidence.txt` probes were refused with their original bytes retained. Updated syntax parsing also passed. No live consumer was prepared, no page call or model task ran, and the earlier 23-check suite was not repeated.
