# Independent C consumer and blind packaging review — first review

This first review is preserved for comparison with any follow-up. It reviews the exact helper versions below, before corrections prompted by these findings. Scope is experiment packaging and provenance only: no actual C Skill contents, consumer answers or execution outputs, other grades, product files or repository history were inspected. No live preparation, model task, business grading or live state operation was performed. No applicable parent-directory AGENTS.md was found.

**Disposition:** consumer preparation and blind grading have separate readiness decisions. The consumer/state path implements the fixed case and state design, and the reviewed consumer schedule exactly matches its deterministic IDs and configuration. One consumer-side preservation gap (F1) needs correction before live freezing/checkpointing. Recording copied file modes would also make downstream comparison reliable. Blind packet preparation should wait for F2–F4. None of these findings infers artifact quality, business adequacy or experimental benefit.

## Findings

### F1 — Non-cache resources can be claimed preserved and then silently omitted by checkpointing

In `prepare_control_consumers.py:artifact_inventory`, only regular `*.pyc` directly under `__pycache__` are excluded, and other resources under that directory are refused. This is the intended treatment for the two creators' reported caches: preserve originals, record excluded paths/hashes, omit the cache bytes consistently from frozen/copied resource identities, and make no durable byte-preservation claim for them. This review did not inspect those creators' files.

However, `checkpoint.py:files` also omits every path containing a `.local` or `.git` component. The current artifact inventory accepts ordinary resources under either component into `file_sha256`. A narrow synthetic check placed `.local/evidence.txt` in a mock supplied Skill: artifact_inventory accepted its bytes, while checkpoint.evidence_files omitted it. This is a concrete mismatch between frozen/copy identity and durable preservation, even though local copytree retains the file.

Before live packaging, explicitly refuse affected non-cache resources for reconciliation or preserve them through an explicit compatible save route. Do not delete, silently drop or classify their quality. Keep the same explicit cache boundary across every downstream evidence inventory/copy. The implementation audit already correctly warns that retained arbitrary binary resources need a separate direct save route if UTF-8 export cannot represent them; that path fails rather than silently omitting bytes.

### F2 — Blind packets omit relevant original and observed evidence

`prepare_control_grading.py` copies a final Skill only when a recorded original file's content hash changed. Added Skill resources and mode-only changes do not trigger that copy or appear in `changed_originals`. It also copies only answer, execution note, prompt, input, work and deliverables from a consumer; other root-level outputs disappear. Creator public execution notes and separately requested demonstrations/implementations outside the supplied Skill are absent altogether.

A single synthetic S06 four-package/eight-application packet had an added non-cache Skill file, a script changed from 0755 to 0644 without changing its bytes, a consumer root result.json, a creator public note and a separate creator demonstration. Packaging exited 0. The added resource, final Skill, root result, creator note and demonstration were all absent from the packet, while resource-observations.json reported an empty changed_originals list. The unchanged frozen package was present, as expected.

Retain a complete final evidence inventory, including additions, deletions and modes, and preserve observed content in the blind packet with original and reported/observed roles kept distinct. Include creator public notes and requested extra deliverables as creator-reported evidence, without promoting their claims into independent checks. Exclude expected runtime caches explicitly; do not let other additions silently vanish. A full source/copy provenance manifest should bind what the grader actually receives.

### F3 — S06 native snapshots are not tied to the consumer, state, label or setup

The native-state helper initializes distinct states correctly and its snapshot method records the consumer, state path, label and SQL hash. Blind preparation currently verifies only the SQL hash from each initial/final JSON record. It neither checks the remaining identity fields nor connects them to the completed setup record and original fixture/interface identities; the setup observation record itself is not supplied.

In the same synthetic packet, every snapshot JSON deliberately named C-U999, wrong-label and /wrong-state/ledger.sqlite while residing under another application's initial/final filenames. Each SQL digest matched its adjacent JSON. Packaging exited 0 and copied the inconsistent metadata unchanged. This could misattribute a committed state to an application.

Require matching consumer ID, label and allocated state path, and bind initial/final evidence to the setup record, original fixture/API identities and assignment's resolved state path. Preserve the setup observations as setup evidence. Graders should receive native SQL and provenance, never a live database. Missing or inconsistent state must remain explicitly missing/inconsistent; do not regenerate an execution result.

### F4 — Blind completion/provenance checks are weaker than the fixed allocation

The pinned grading allocation and complete 29-file consumer bank are checked, but the grading helper reads mutable creator/consumer ledgers only for an execution=completed value. It does not verify either fixed schedule/digest, ledger assignment fields, consumer configuration/context, or assignment consumer_id. It checks prompt existence but not its recorded hash. Frozen package and snapshot roots/ancestors are not consistently checked for symlinks, although inner file symlinks are rejected. These omissions weaken provenance independently of any quality judgment.

The synthetic packet's prompt was deliberately changed after its recorded assignment hash was computed; packaging exited 0 and copied the changed prompt without an inconsistency record. Schedule/ancestor omissions were identified by source inspection; no additional fault matrix was run. The consumer helper itself pins and checks the full creator schedule, verifies selected creator assignment/input/prompt identity, and performs whole-batch owned-path refusal. It derives the correct consumer IDs/configuration but leaves the separate consumer schedule/ledger to the coordinator; a consistency preflight should keep those records tied together.

Before blind use, verify both fixed schedule identities and exact ledger mappings, retain explicit completion as an observation, and validate assignment/freeze/prompt/state links. Apply the same regular-path/ancestor refusal to evidence sources and owned destinations. Preserve any partial output for reconciliation. Do not infer missing completion or quality from file existence.

## Confirmed properties and limits

- Read-only checks found exactly 72 creator cells in ascending family, prescribed model, low/high and repetition order, and exactly 144 ordinary/challenging consumer rows. Every consumer row equals the helper's C-U{2n-1}/C-U{2n} mapping at fresh gpt-5.6-sol/high; the schedule/digest and grading allocation hashes below match their documented identities.
- All 29 consumer-bank files match the frozen manifest. S01 ordinary/challenging requests match their calibration sources exactly. Both S05 two-file inputs and both S10 request/state pairs match their development sources exactly. These are reused stimuli, not new holdouts.
- Consumer preparation requires explicit completed creator IDs; verifies the original public bank and selected assignment/input/prompt identities; freezes supplied resources before materializing either consumer's case; checks source/frozen/consumer bytes; and uses copy2/copytree to preserve modes. The implementation's disposable output reports exact executable-mode preservation. The freeze manifest records source modes; this initial version lacks corresponding copied-mode metadata and later mode comparisons.
- The consumer preflight rejects existing/partial freezes, consumer folders, external assignments, setup records, snapshots and native-state allocations, including dangling symlinks and unexpected parent entries, before any selected batch writes. Later failure preserves partial work. The implementation audit's 23 narrow setup/copy checks were read; they were not rerun. Source inspection agrees with its reported boundaries.
- Only reviewed input directories are given to consumers. S06 fixture data, setup call records, initial SQL and all oracles stay outside consumer task folders. Creator assignments and control mappings remain outside task contexts. The common optional skill-creator has seven recorded text-resource hashes checked; two previously unrecorded display assets get current hashes without an original-identity claim. Procedural read restrictions do not enforce shared-filesystem isolation.
- S06 receives the exact frozen ledger API. Setup uses a uniquely allocated SQLite file per application, verifies the fixture-derived snapshot and record count, and checks tranche 1 with two remaining calls using init/describe only. It does not spend page calls or grant another tranche. The snapshot uses mode=ro, an explicit BEGIN and a successful quick_check before iterdump, giving a consistent committed logical state. It does not establish runtime-byte identity, full call history, response incorporation, or business completion. Native SQL cannot recover work after the last preserved snapshot or replace missing continuation evidence; no live state was reset or recovered in this review.
- S10 receives the exact frozen release interface plus its own copied original state. The allowed path substitutions bind environment-path to that consumer's input folder and state-path to its state.json. Raw candidate, environment, owner approval, qualification, timeout and request-ID bytes are unchanged. Original and final JSON states remain distinct evidence sources.
- validate_control.py applies the existing pinned physical Agent Skill validator only after explicit creator completion and preserves one exclusive report. It supplies no ALPS heading, vocabulary, semantic or effectiveness criterion. This review did not run it against a C artifact.
- Blind grouping uses four preallocated packages and both applications per packet, with coordinator-only identity mapping. The grading plan preserves the preselected independent second sample and consequential second review. Original embedded paths can disclose provenance hints; this is limited identity blinding, not complete removal of attribution clues. Primary/secondary independence, disagreement and missingness still require coordinator execution.

## Bounded independent observations

The only new executable observations were (1) one synthetic blind packet to resolve F2/F3 and the prompt part of F4, and (2) one synthetic non-cache inventory comparison for F1. The helper was copied unchanged with SHA-256 70638868bb15f9ef58114f7f502189b8f0f2d65c6971126f646a766bef8f6fb1. The fixture used copied raw case banks/oracle/business inputs and fabricated Skill/answer/observation/state evidence, never actual C output. It ran no model, API or synthetic business operation. The temporary tree is /tmp/control-packaging-review-7ljtp9ti and its public result is check-output.json. No existing file was removed or helper edited.

The blind command was `python3 -B /tmp/control-packaging-review-7ljtp9ti/evidence/prepare_control_grading.py S06-P01`. It exited 0 with no stderr and reported four packages/eight observations. The observed final flags were: added_skill_resource_preserved=false; observed_final_skill_preserved=false; root_consumer_result_preserved=false; creator_public_note_preserved=false; creator_demo_preserved=false; changed_originals=[]; changed_prompt_accepted=true. The copied final snapshot metadata named C-U999 / wrong-label / /wrong-state/ledger.sqlite with SQL SHA-256 1713c49c104819a7df7cee6a37a4417723e339a8fd20952b8ba8483eb7730079. For F1, consumer_inventory_accepted=true and checkpoint_inventory_preserved=false.

No broad test suite or repeated model/application experiment was performed. These observations are infrastructure evidence only.

## Exact reviewed file identities

SHA-256 values were read directly from the files listed. The source, schedule and manifest checks occurred before the prompted corrections; later edits require a separate follow-up review rather than replacing this record.

| Reviewed path | SHA-256 |
| --- | --- |
| `prepare_control_consumers.py` | `f6bba138b7c1920c73a70eca7065a435eb9ca2e074648dd52ddbf14177ebc642` |
| `control_ledger_state.py` | `d882ca0323dd6e8887017b74ea1dc7adc06bd8cd1c0b3b92deda00c26932094d` |
| `validate_control.py` | `c62f075604e6c11921f8a152f20b68615783296e1a59f0b28162d95c14791d0f` |
| `prepare_control_grading.py` | `70638868bb15f9ef58114f7f502189b8f0f2d65c6971126f646a766bef8f6fb1` |
| `prepare_consumers.py` | `29d4ac2e4f1ada625f7bc6938c31b47e5bc0e563dc6e8e8a7e5c9a45c74f8cf3` |
| `prepare_control_fixed_cases.py` | `d871300ad951609f444b02bd633807767b1a095dc1c69e938a0b21123f6fafed` |
| `checkpoint.py` | `8153f3cf02db0f3877e988114d99c94b24133418533c08c2dd70ad3d882b9b42` |
| `control-stage.md` | `9d6823aef675543948c6fef06db1cd9b5fb72ad9e678b0562768ee16ef3cc5f4` |
| `control-case-provenance.md` | `5eed3c670089cbe1669cce8404b720d346ff67bdde88d5e8785e6e7dae72a1a8` |
| `control-grading-plan.md` | `90786308e956894c38cb8355b7c94b34e685f339e69a838b79b636d852d3a97f` |
| `grading-guidance.md` | `35e3fcadda5f885a6ad346961c56e3d15127a6379155ab0de8f4e397958e9afe` |
| `control-schedule.tsv` | `739210b57f1b000dcb3cf6f4e2ee912ca6e911d8e829eacde225bb03ffe91569` |
| `control-schedule-sha256.txt` | `589bec88d99765e6f0b32fa1168f725a2d544fa8f62137f62f7faf7de1fa7a60` |
| `control-consumer-schedule.tsv` | `6321c8bbbfaf1dcd0c3ae6d118b52480c9f5e13897f34196fb1b547d7cd7a6c0` |
| `control-consumer-schedule-sha256.txt` | `c08cd62916a7f6cd3efcd8e78c23e370606a251dab4d6dbe67a801c7ff863707` |
| `control-grading-allocation.json` | `bb463eceeccea6502418daf3263558d386c8fd31f4b1dcfe4f5fba411c577a0f` |
| `main-case-hashes.json` | `142cc29cef88dd33d93b682ff596b68968cf3033d6887eadad509aa8e2cb9fd4` |
| `frozen-hashes.sha256` | `dba1fcdde399d5f0c6a65526ecf2a3ce880ab2bf2b6cd340e90aaed44b5cd32c` |
| `control-consumer-case-hashes.json` | `f26be07f6cfba54aedc3068a67ae32292877f6ee005f0c190156f5786d1cbdc2` |
| `control-oracle-hashes.json` | `e989aca00c688f58d997377dbf97c7d030aad6ca629cd94bb5835339297456b4` |
| `frozen/main-cases/S06/brief.md` | `62f310f50ff7280749ada5871746d154005f82fc11aae85dff8bb31c5f7b1b1b` |
| `frozen/main-cases/S06/fixture.json` | `d2ad6670cd561401486548b5702d1734ef280822a5651431461647a8710a675a` |
| `frozen/main-cases/S06/ledger_api.py` | `4622ec041dcfe8057aed319bc0ad168f24aebf4520a68c2961cdf046483315f3` |
| `frozen/main-cases/S10/brief.md` | `284eab48172c8b996d5eb3218590fb453c1e24f5b532f9d4457bda99fb38485e` |
| `frozen/main-cases/S10/release_tool.py` | `939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577` |
| `audits/control-consumer-packaging-implementation.md` | `0114570e0d0d87882ddbae7cef8ba13e0b6051583e8282ce2bcde692dbc01fe0` |
| `audits/control-consumer-packaging-check-output.json` | `87b37f42516aaff4041326a34c27d302f813cda6188d3beacc99d56024e286e6` |

| Raw S06/S10 consumer source | SHA-256 |
| --- | --- |
| `control-consumer-cases/S06/challenging/fixture.json` | `f47ce9c9aa4f114cc21fc2c069be45cb949b68c0aa08a324969c5b00a5821c29` |
| `control-consumer-cases/S06/challenging/input/request.md` | `498d7b5bc06d41fecba1fd19e00f529b35fd633c6586d83f086814f5954e2db9` |
| `control-consumer-cases/S06/ordinary/fixture.json` | `202822ea97ff2b7850d3a06eb6b3770e18936a336c0e64725c9a3c7da2709f19` |
| `control-consumer-cases/S06/ordinary/input/request.md` | `724929c06b67118a4f9468d1351c627b7396a03f1ed983c7cf23e2ab90988b09` |
| `control-consumer-cases/S10/challenging/input/request.md` | `23ca57f9b4c4d0e6c05dfe4e8799509c2de4738c1052144265b9eba3e84775b2` |
| `control-consumer-cases/S10/challenging/input/state.json` | `88113554cedb729543be2f86c47663a8a14bcd95ef9d3a9ba038242eeddcb4c2` |
| `control-consumer-cases/S10/ordinary/input/request.md` | `3122fa3da2dd1c9e642c1f6b75db9f9d01668de14da6026cad91ef81d676210d` |
| `control-consumer-cases/S10/ordinary/input/state.json` | `94bdfeb6c040ffcc7713ce93762bdb72fa18c065dafc6bbbc6f8f57f554f4c49` |

