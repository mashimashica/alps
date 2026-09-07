# Local stock-evidence command, version 2.0.0

The receiving tools owner supplied `tools/stock_evidence.py`. Python 3 and its standard library suffice; there is no package install, network access, database, environment-variable configuration, or service to launch. Run relative to this case directory, or substitute the actual absolute paths:

```sh
python3 tools/stock_evidence.py --version
python3 tools/stock_evidence.py --help
python3 tools/stock_evidence.py --manifest demo/manifest.csv --count-events demo/count_events.csv
```

The command reads the named files without modifying them and emits one JSON evidence object to standard output. A consumer may capture that output in a local artifact. It does not read quality context and has no stock-write or release capability.

## Accepted inputs

Both files are UTF-8 CSV, with optional UTF-8 BOM. Required headers may appear in any order. Additional named columns are ignored; duplicate or empty header names and rows with extra unnamed cells are rejected. The required columns are:

- Manifest: `manifest_line_id,site_id,shipment_id,sku,lot_id,expected_qty`
- Count events: `event_id,site_id,shipment_id,sku,lot_id,quantity,condition,state`

Required identity and row-ID fields must be nonempty after trimming. The four matching IDs are trimmed and uppercased; their leading zeros are preserved. Opaque manifest-line IDs and event IDs are trimmed but remain case-sensitive. A repeated manifest-line ID or repeated event ID anywhere in its input is rejected, even if the repeated row is identical; separate legitimate additive lines must have distinct row IDs.

Quantities are ordinary signed base-10 decimals with at most nine digits before the decimal point and at most three after it. Scientific notation, thousands separators, nonfinite values, and surplus precision are rejected. The lexical form has no redundant leading zero except for zero itself; identifiers are not subject to that numeric rule. Expected quantities must be nonnegative. Count quantities may be negative because they are additive corrections. Arithmetic uses integer thousandths, with no binary floating-point rounding. This representational precision is not permission to release fractional pieces under SW-RCV-04.

`condition` is `good` or `damaged`; `state` is `posted` or `pending`, compared after whitespace trimming and lowercasing. Posted count changes are summed by condition. Pending events are retained as references but are not included in posted totals. No supersession or reversal is inferred from a note or from file order; a correction must be represented by the supplied signed quantity and state.

## Evidence returned

Version 2 performs a full outer match by the four matching IDs, combining repeated manifest lines and posted count changes. The JSON contains a tool name, version, input row counts, key field names, and sorted `groups`. Each group contains:

- `key`: the normalized four-field identity;
- `manifest_qty`: summed expected quantity, or `null` if there is no manifest evidence;
- `posted_good_qty` and `posted_damaged_qty`: net posted quantities, or both `null` when there are no posted count events for the group;
- `good_minus_manifest_qty`: the arithmetic difference, or `null` if either required side is absent;
- sorted `manifest_line_ids`, `posted_event_ids`, and `pending_event_ids` for lineage;
- mechanical `flags` for a missing manifest, missing posted counts, pending events, or negative net posted totals.

All non-null quantity values are decimal strings. A zero good or damaged total is meaningful only when there is posted count evidence; the explicit missing-side handling avoids treating absent records as zeros. Group and reference ordering is deterministic, not the input row order.

Malformed CSV, duplicate source IDs, missing required values, unsupported states, invalid quantities, and unreadable inputs cause exit code 2 with a JSON error on standard error and no partial evidence on standard output. Argument-usage errors follow Python's normal command-line usage output and also exit 2. A valid run exits 0, including when groups have missing-side or other evidence flags. Those flags describe the input; they are not release decisions. An empty pair of correctly headed inputs is a valid zero-group packet, not a claim that a real shipment is cleared.

## What did not improve

The command cannot establish that a source is authentic, complete, the latest authorized export, or an accurate physical count. It cannot detect a missing event that was never supplied. It does not evaluate current quality context, whole-piece business requirements, approvals, release authority, or all of SW-RCV-04. It cannot infer missing IDs, settle contradictory business evidence, or approve a count correction. The old row viewer did not have version 2's interface; do not silently assume it is compatible if version 2 is unavailable.
