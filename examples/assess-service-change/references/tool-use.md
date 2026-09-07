# Measurement tool

[Japanese translation](locales/ja/tool-use.md)

The [script](../scripts/compare_measurements.py) reads two local CSV snapshots, validates them, calculates request metrics, and evaluates the supplied numerical limits. Python 3.11 or later and its standard library are the only dependencies. Invoke from the example Skill directory, or use absolute paths for the script and input files.

```console
python3 scripts/compare_measurements.py assets/baseline.csv assets/candidate.csv --min-samples 4 --max-p95-ms 200 --max-error-rate 0.05 --max-p95-increase-ms 50
```

Use `--help` for the argument interface. Select the limits from the applicable [pilot conditions](pilot-context.md). The tool requires explicit limits so the caller can identify which criteria its comparisons implement.

Both files must be UTF-8 CSV with exactly the ordered header `request_id,duration_ms,status`, at least one row, unique nonempty request identifiers within each file, finite nonnegative numeric durations in milliseconds, and `status` equal to `ok` or `error`. Requests need not have matching identifiers across the two measurement runs. Malformed or incomplete rows are rejected. The minimum sample count must be positive, error proportion must lie between zero and one, and duration limits must be finite and nonnegative.

Standard output is one JSON object containing the supplied limits, each file's path and SHA-256 digest of the bytes read, counts, error proportion, nearest-rank p95, the p95 change, and Boolean results for each numerical comparison. This is the interface of this example tool. A sample below the requested minimum is valid input but fails its sample-count check. Exit status `0` means calculations completed, including when one or more limits were not met; it does not mean the pilot criteria have been established. Exit status `2` reports invalid arguments, invalid measurements, or unreadable files on standard error and emits no result object.

The operation reads files and writes only to standard output/error. It does not change the inputs, deploy a service, or call a network service. It reads each file once, identifying that snapshot by its digest. Use stable copies when simultaneous measurement updates are possible. Repeating with the same bytes and limits produces the same metrics and checks; paths in the response may differ. Fix the indicated input or access problem before retrying a failed read or validation.

The agent must relate numerical checks to measurement context, applicable criteria, and the work's Outcomes. Successful JSON production cannot establish comparability, the truth of measurement provenance, or suitability beyond the specified pilot.
