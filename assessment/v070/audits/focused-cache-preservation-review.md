# Focused runtime-cache preservation review — 2026-09-08

Direct checkpointing can resume for the reviewed change. The only additional omissions are the exact 76 recorded verification bytecode files. All observed evidence remained readable as UTF-8, and direct export completed in memory without a remote write. Changed cache bytes, mismatched magic, an out-of-prefix entry, a Skill resource, and a path escaping the permitted prefix were each refused on disposable fixtures.

## Scope and identities

This review compared `checkpoint.py` with `/workspace/scratch/a75c3a6d9076/assessment-checkpoint-MQcRsS/checkpoint.py` and inspected only the added runtime-cache omission boundary. The native SQL route and existing exclusions were not changed by this delta.

| File | SHA-256 |
| --- | --- |
| Prior checkpoint helper | `f98c1d24cc219e87de9467bb94289853ae32885ee40fce36f2aa743dc8ac6e30` |
| Reviewed checkpoint helper | `b75eb7e29aab9cadd0f362e0cfbfd4ef760a29ef141e2230bcfbcfb2f250478d` |
| `focused-runtime-cache-omissions.json` | `6571e434dbe01f986a0079f53cf3df8d8b83dcffb48cd56b58968b4629662516` |
| `trials/focus-005/execution-note.md` | `35d549f000028328c29cb7f8dfa77b359902dfe1eaf7f3c9ac73be232aac2ecf` |

The code validates every indexed file before omitting any: it requires one of the two fixed focus-005 verification-cache prefixes, `.pyc`, a regular resolved file, at least a 16-byte header, matching recorded magic, and exact recorded SHA-256. The omission uses exact manifest membership rather than a prefix-wide skip. The index itself remains in exported evidence. This verdict applies to the reviewed helper and manifest; it does not authorize arbitrary future manifest additions.

## Actual files and creator corroboration

The manifest's 76 paths exactly equal the complete actual file sets beneath `trials/focus-005/.verification/pycache/` and `pycache-final/`: 38 files per directory, 878,304 bytes per set. Every file is regular, resolves to its own path, has the recorded SHA-256 and mode 0644, and starts with `cb0d0d0a`, matching the local CPython 3.12.13 magic. Reading each marshal payload as data, without executing it, yielded a Python code object: 37 runtime-module sources and one compiled `rollup_ledger.py` source per set.

The creator note explicitly records `PYTHONPYCACHEPREFIX=.verification/pycache-final python3.12 -m py_compile deliverables/skills/reimbursement-ledger-rollup/scripts/rollup_ledger.py`, exit 0 with no output. It also states that disposable bytecode was kept under `.verification/`. The note does not separately transcribe the initial `pycache/` invocation; its broader location statement, the exact cache inventory, and the code-object source names corroborate that set without inventing another captured command.

The manifest records present file modes; the runtime omission guard enforces path, content hash and magic, not mode equality. These are intentionally omitted runtime bytes retained locally, not a claim that their bytes have been durably preserved. No source cache was moved, deleted, encoded or modified by this review.

## Concrete export and refusal checks

At 2026-09-08 01:32:50 UTC, the old helper enumerated 7,391 evidence files against the current tree and the new helper enumerated 7,315. The exact set difference was the 76 manifest entries, with no other added or removed path. All three focus-005 supplied input files and all three generated Skill resources remained in the export inventory.

Every file in the new inventory decoded as UTF-8. Calling the actual `export()` function with stdout captured in memory produced 485 valid plain-text Git blob entries; no recorded cache path entered that export. The frozen-source verification passed and the native SQL index remained unchanged during the check. Counts precede this review's two new text audit files.

Five disposable cases were created outside the assessment at `/workspace/scratch/a75c3a6d9076/focused-cache-review-vq6leoa_`:

| Counterexample | Result |
| --- | --- |
| One changed byte with unchanged manifest hash | Refused: observed runtime cache changed |
| Recorded magic differing from actual bytes | Refused: observed runtime cache changed |
| Same bytecode indexed under focus-006 | Refused: unexpected runtime-cache omission |
| Same bytecode indexed inside the generated Skill | Refused: unexpected runtime-cache omission |
| Indexed prefix containing `..` traversal into deliverables | Refused: unexpected runtime-cache omission |

All 76 original cache hashes still matched afterward. No business task, cache-producing command, SQLite creation, remote write, checkpoint `mark`, or cached export operation was run. Only textual observations were added inside the assessment. Exact export counts, protected resource paths, counterexample paths and refusal messages are preserved in `audits/focused-cache-export-observation.json`.
