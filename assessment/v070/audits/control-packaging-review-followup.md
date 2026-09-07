# Independent C packaging review — bounded follow-up

The four findings in `audits/control-packaging-review.md` are resolved within the reviewed packaging scope. Consumer preparation at `4a3cfe4e...` and blind preparation at `d0af475a...` have separate readiness: the consumer helper was already cleared after its source/metadata correction, and the final blind helper now passes the specific follow-up below. No remaining blocker was found for the exact three-entry SQLite preservation integration examined here. Checkpoint success and explicit task completion remain coordinator observations, not implications of this review.

The first review remains unchanged at SHA-256 `0de08e91dc714a59d22776216524f70a086b927b16be191875cce69113f71995`. Its original grader source is additionally archived byte-for-byte in `audits/control-packaging-review-initial-grading-source.txt`, still hashing to `70638868bb15f9ef58114f7f502189b8f0f2d65c6971126f646a766bef8f6fb1`. The old synthetic tree and its source/check output remain intact under `/tmp/control-packaging-review-7ljtp9ti`; the check result is also retained in `audits/control-packaging-review-initial-check-output.json`. The first failing observations are not attributed to the corrected implementation.

No actual C Skill contents, actual consumer results, other grades, product code or repository history were inspected. No model, consumer business operation, live preparation or live state mutation was performed. This follow-up edited only review artifacts.

## Disposition of F1–F4

| First finding | Follow-up disposition |
| --- | --- |
| F1: checkpoint-omitted non-cache resources | Resolved. The consumer helper explicitly refuses resource paths containing .local or .git and non-cache content under __pycache__, including an affected Skill directory name. It leaves originals untouched for reconciliation. Blind inventory and copy operations reuse the same regular-path/resource/cache rules. Regular .pyc files directly under __pycache__ are recorded as excluded original runtime caches and omitted from both copied resources and their saved identities. |
| F2: missing original/final evidence | Resolved for the identified gaps. Final Skills are copied with added resources and observed modes; resource observations record additions and changes/deletions to original bytes/modes. Other root consumer files, creator public notes and non-Skill creator deliverables are preserved separately. Creator notes stay labelled as reported checks. An external packet provenance file records every copied resource's hash and mode plus the excluded original caches. |
| F3: misbound S06 snapshots | Resolved. Consumer assignments now anchor setup JSON plus initial SQL/JSON hashes. Blind preparation validates the exact initial path set and hashes; setup consumer ID, verified status, fixture/API hashes and allocated state path; and each initial/final label, consumer ID, state path and SQL hash. Setup observations accompany the committed SQL evidence. |
| F4: weak schedule/prompt/source links | Resolved for the recorded gaps. Both fixed schedules/digests and complete ledger assignment fields are checked. Consumer identity, creator, variant, case, requested model/effort, fresh context and freeze hash are checked, as are the original prompt hash and completeness of the copied mode map. Evidence trees and JSON/file-copy sources use the reviewed regular-path/ancestor checks; creator extra deliverables are inventoried before copying. Existing/partial packet, mapping or provenance destinations refuse replacement. |

The final code also compares source and copied tree hashes/modes after copy. Source-root symlinks and unsupported filesystem entries are rejected through the shared inventory. It preserves partial output if a later copy fails; it does not silently repair evidence or infer quality from packaging success.

The consumer helper's narrow metadata follow-up output was read in full. All four fabricated consumers had mode keys identical to byte-hash keys, with observed 0755 and 0440 modes recorded correctly. Both synthetic S06 assignments anchored exactly the setup and initial SQL/JSON files; non-S06 maps were empty. Separate non-cache .local/.git resources refused. The earlier 23-check implementation exercise was not repeated.

## Independent follow-up observations

One new synthetic S06 packet addressed the exact omissions and provenance gaps. It used only the preserved first-review fixture tree, copied raw inputs/oracle and fabricated package/application evidence. The current grader, consumer helper and ledger helper were copied unchanged into a new disposable tree. No generated C package, original verification database or live consumer workspace was used.

Before its successful run, the same fixture exercised the two directly implicated refusal paths separately. A wrong final snapshot consumer ID failed with `Native state evidence differs: C-U095/final`; a prompt changed after its recorded hash failed with `Original consumer prompt changed: C-U095`. Both exited 1 before any packet directory existed. The deliberately changed synthetic inputs and their output observations were retained; then the valid synthetic inputs were restored for the positive packaging check.

The corrected packet command was:

```sh
python3 -B /tmp/control-packaging-followup-3d6tp63r/evidence/prepare_control_grading.py S06-P01
```

It exited 0 with no stderr, creating the prescribed four packages and eight synthetic observations. Readback confirmed:

- All 146 packet resource hashes and modes exactly matched its external provenance manifest.
- An added Skill resource and a byte-unchanged script's 0755-to-0644 mode change were preserved and recorded.
- An extra consumer root result, creator public note, separate creator demonstration and S06 setup observations were present.
- No .pyc cache byte appeared in the packet. The 20 recorded source cache groups pointed to unchanged original synthetic files. Cache exclusions did not appear as preserved packet bytes.

The precise captured results are in `audits/control-packaging-review-followup-check-output.json`; the disposable tree remains at `/tmp/control-packaging-followup-3d6tp63r`. These are packaging checks, not fresh model applications, component business validation or effectiveness evidence. No broad fault matrix was added.

## Narrow SQLite durability integration

The new preservation route addresses three explicitly named, completed creator verification databases, outside the supplied Skill and consumer state. Its scope does not turn logical SQL into preservation of arbitrary binary Skill-resource bytes.

`preserve_sqlite_evidence.py` checks a native SQLite header, refuses observed WAL/journal files that require separate preservation, opens the source with mode=ro, and uses BEGIN plus a successful quick_check before iterdump. It compares the source byte hash before and after preservation. SQL and metadata paths are created exclusively; a prior complete or partial observation is retained. The metadata and index identify the source hash, SQL hash, metadata hash and SQLite version and explicitly claim only committed logical state. Original binaries are left untouched. This is not a source reset, a replay of verification work, a complete operation history or a byte-identical database backup.

`checkpoint.py` excludes only the exact source paths represented by the explicit index. Before doing so, it validates the SQL/metadata target locations and hashes and checks the source hash when the original binary is present. A changed source or missing/changed representation stops export. Nonindexed non-UTF-8 resources still stop plain-text export; the change is not a blanket exclusion for SQLite or binary files. SQL/metadata and the index themselves remain ordinary checkpoint evidence. After recovery from the saved text evidence, an absent original binary is permitted by this route; the recorded source hash remains provenance, not a claim that those binary bytes were recovered.

The three current index entries are exactly:

| Completed verification source | Representation |
| --- | --- |
| trials/control-037/verify1/source.sqlite | Native SQL plus metadata under sqlite-evidence/creator-complete/ |
| trials/control-037/verify2/source.sqlite | Native SQL plus metadata under sqlite-evidence/creator-complete/ |
| trials/control-037/verify3/source.sqlite | Native SQL plus metadata under sqlite-evidence/creator-complete/ |

I read `audits/sqlite-evidence-preservation-check.json`: all three root-performed read-only/in-memory checks report equal logical dumps and unchanged source bytes. I did not repeat those valid checks or inspect source database contents. My additional read-only check covered only the exact index and six SQL/metadata file identities: each source_path matched its index key, each metadata record matched the index, all representation files were regular files at canonical assessment paths eligible for checkpoint export, and all six recorded hashes matched. None lay under .local, .git or __pycache__. That result is retained in `audits/control-packaging-review-sqlite-identity-check.json`.

These checks establish the stated representation for these three entries, not general byte preservation, recovery of unsaved work, or business-validation quality. This follow-up did not execute a checkpoint, Git mutation or external save; successful durable checkpointing remains the coordinator's separate gate.

## Remaining interpretation limits

The first review's limits remain: shared-filesystem access restrictions and identity blinding are procedural; embedded original paths may reveal provenance hints. Native SQL preserves the observed committed representation, not unrecorded calls, response incorporation or later work. Original and final S10 state are separate evidence; state transitions still need business review. Public notes may be incomplete reports. Physical format, component quality, consumer task adequacy, business result, satisfied conditions and evidenced compensation remain separate judgments. The helpers do not establish C performance, qualify B, reopen ordinary development or satisfy dependent release gates.

## Exact reviewed and preserved identities

| File | SHA-256 |
| --- | --- |
| `audits/control-packaging-review.md` | `0de08e91dc714a59d22776216524f70a086b927b16be191875cce69113f71995` |
| `audits/control-packaging-review-initial-grading-source.txt` | `70638868bb15f9ef58114f7f502189b8f0f2d65c6971126f646a766bef8f6fb1` |
| `audits/control-packaging-review-initial-check-output.json` | `b48dda5f1a1db8f745896b38c31fbe5ece9576b5bfde9184f47decb946997d36` |
| `audits/control-packaging-review-followup-check-output.json` | `dccd4ffdbb1406b46c99cdaefbf3ccac1718a70c4d6068c5f15a1cc576341974` |
| `audits/control-packaging-review-sqlite-identity-check.json` | `10941dd09d78ac1fa087a2cf71817117b79264cb236f4c1755c99d3225ef4c90` |
| `prepare_control_grading.py` | `d0af475ae5f6809273232c5b49800772845e2bfbff1b71d33880892f485c0c1f` |
| `prepare_control_consumers.py` | `4a3cfe4e641d91c90348b19f128b6e281b898414d0ff157538d550f5f51ca32c` |
| `control_ledger_state.py` | `d882ca0323dd6e8887017b74ea1dc7adc06bd8cd1c0b3b92deda00c26932094d` |
| `validate_control.py` | `c62f075604e6c11921f8a152f20b68615783296e1a59f0b28162d95c14791d0f` |
| `preserve_sqlite_evidence.py` | `3c024f1cf763da4701fa198892b6dd6c0fb9a59fc445c8ef5e6d7768f8707f6c` |
| `checkpoint.py` | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |
| `sqlite-evidence-index.json` | `3614aa1659cef948bc6552ffc92011d68de91790cadc3f3814c17bac9e91533b` |
| `audits/sqlite-evidence-preservation-check.json` | `f4ec91231ac0e9433e8dd42b580a2a156bc60ed71a932bdbb01345a6fbfa8df6` |
| `audits/control-consumer-packaging-implementation.md` | `5a9e5036780e7433c191127c47213535250f9faaa1f337ab9e12af7f249816dc` |
| `audits/control-consumer-packaging-metadata-check-output.json` | `206844e46ccf14b69a03401cab43f069eee4fc8b15ac2383e7afed8a561b9ed4` |
| `sqlite-evidence/creator-complete/trials/control-037/verify1/source.sqlite.sql` | `219e63be90b1d1eb5c8e921ba5474934bd30a8fedf2bdb687eb18f441e5397e8` |
| `sqlite-evidence/creator-complete/trials/control-037/verify1/source.sqlite.json` | `17fb4b88117fb3e87d85615095f749b223f860ea8467cb48d2d67b06c33d9f6a` |
| `sqlite-evidence/creator-complete/trials/control-037/verify2/source.sqlite.sql` | `6f349b0986fd242c4479a8b1497f8eda60ed553091b8f2aa2f2d8e433cad0f56` |
| `sqlite-evidence/creator-complete/trials/control-037/verify2/source.sqlite.json` | `b79d368bd1029236070fba5f7a8d2987bf19e43f7b9f2d6ca2be02dd94c2b2e4` |
| `sqlite-evidence/creator-complete/trials/control-037/verify3/source.sqlite.sql` | `76663ce0dc1bcdd9daca679aa9f5665e38123a58a5213bab37e4a414cd1ec479` |
| `sqlite-evidence/creator-complete/trials/control-037/verify3/source.sqlite.json` | `f585919396a632e43278a5efa90784c7e4b342ec3baf292a78df64076a00417f` |

