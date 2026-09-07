---
name: reimbursement-rollup
description: Produce complete, exact vendor reimbursement rollups from an immutable paginated ledger for an inclusive posting-date interval, with durable continuation across operator-approved call tranches.
---

# Reimbursement rollup

Use the bundled [runner](scripts/rollup.py) with Python 3.12 on a POSIX system. It uses only the standard library and the supplied ledger API CLI; no package installation is needed. The caller supplies an existing source state, the API script path, an inclusive start and end date, and a dedicated writable checkpoint path. The checkpoint holds ledger entry identifiers and vendor totals; keep it access-controlled and retain it until the request is finished. Do not share a checkpoint between different requests.

Run (replace all example paths with absolute paths):

```sh
python3.12 /path/to/reimbursement-rollup/scripts/rollup.py --api /path/to/ledger_api.py --state /path/to/source.sqlite --start 2026-02-01 --end 2026-02-15 --checkpoint /path/to/request.json
```

The API and existing source state are operational dependencies, not bundled data. Never obtain operational entries by reading fixtures or querying the source database. Do not initialize or reset an existing state. The runner invokes only `describe` and `page`; it never grants a tranche.

## Interpret output and continue

- Exit 0 and `status: complete`: final result, including snapshot, date interval, USD integer-cent totals, sorted vendor rows and examined source count. Completion requires both a null next cursor and equality with the source record count. Empty results are valid. Keep zero and negative net vendors.
- Exit 75 and `status: incomplete`: quota boundary; `partial_vendors` are provisional, never a final rollup. Tell the analyst coverage is incomplete, report examined versus total entries, preserve the checkpoint, and request another operator-approved tranche. The operator separately grants it through the source control. Re-run the identical command after approval. Without approval the request remains incomplete indefinitely; do not promise completion.
- Exit 2 and `status: error`: invalid input, source failure, inconsistent response, checkpoint mismatch or storage error. Do not describe any totals as final. Preserve the checkpoint and investigate the reported detail. A source call may have consumed quota even if no response was received. Resume the identical command once the problem is resolved; never assume retrying is free.

Dates must be real calendar dates in exact YYYY-MM-DD form with start no later than end. Invalid intervals are rejected before source traversal. Pending and void rows never contribute. For settled rows within the interval, add charges and credits separately using integer cents, and compute net as charges minus credits. Qualifying count includes both kinds, including zero amounts. Examine every page regardless of row dates or source order.

## Checkpoint and recovery guarantees

Each accepted page updates the cursor, examined identifiers and totals together through an atomic, fsynced checkpoint replacement. A crash before replacement leaves the previous page boundary; retry requests the same opaque cursor, paying another successful call if needed, and incorporates it once. A crash after replacement resumes at the next cursor. Null is distinguished from the initial cursor by a completion flag. A lock serializes runners using the same checkpoint. Repeated invocations after completion use the saved result without further page calls.

The runner binds the checkpoint to the API path, state path, interval, snapshot and record count. It rejects duplicate IDs across accepted pages and cursor cycles rather than silently certifying questionable coverage. It checks quota before each page and also respects source exit 75. Never edit checkpoints or run the same request with competing checkpoint paths as a recovery technique. Do not grant/reset tranches concurrently with a running command. Other source consumers can spend shared quota; exhaustion still pauses safely.

Limits: local durable filesystem semantics and an honest immutable API contract are assumed. A lost/deleted/corrupt checkpoint needs operator-led recovery and may require traversal again; metadata alone cannot reconstruct incorporated pages. Storage grows with examined IDs and cursor history, and checkpoint rewriting costs grow with ledger size. No remote checkpoint, automatic approval, or distributed locking is provided. The tool does not promise exactly-once API calls, only atomic incorporation into its local result.
