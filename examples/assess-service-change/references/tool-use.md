# Measurement tool

[Japanese translation](locales/ja/tool-use.md)

The [script](../scripts/compare_measurements.py) reads two local CSV snapshots, validates them, calculates request metrics, and evaluates the supplied numerical limits. Python 3.10 or later and its standard library are the only dependencies. Invoke from the example Skill directory, or use absolute paths for the script and input files.

```console
python3 scripts/compare_measurements.py assets/baseline.csv assets/candidate.csv --min-samples 4 --max-p95-ms 200 --max-error-rate 0.05 --max-p95-increase-ms 50
```

Use `--help` for the argument interface. Select the limits from the applicable [pilot conditions](pilot-context.md). The tool requires explicit limits so the caller can identify which criteria its comparisons implement.

Both files must be UTF-8 CSV without a byte order mark, with exactly the ordered header `request_id,duration_ms,status`, at least one row, unique nonempty request identifiers within each file that contain only printable characters and have no leading or trailing whitespace, durations in milliseconds written as nonnegative decimal numbers (digits with an optional fractional part, such as `100` or `12.5`) within the finite floating-point range, and `status` equal to `ok` or `error`. The tool reports whether both files contain the same set of request identifiers; whether those identifiers represent the same fixed request set remains a judgment from the measurement context. Malformed or incomplete rows are rejected. The minimum sample count must be a positive integer written with ASCII digits only, the other limits must be written in the same decimal form as durations, and error proportion must lie between zero and one.

Standard output is one JSON object containing the supplied limits, each file's path and SHA-256 digest of the bytes read, counts, error proportion, nearest-rank p95, an `input_relationship` object, the p95 change, and Boolean results for each numerical comparison. In `input_relationship`, `identical_bytes` reports whether the two digests match, and `same_request_ids` reports whether both files contain the same set of request identifiers. This is the interface of this example tool. A sample below the requested minimum is valid input but fails its sample-count check. Exit status `0` means calculations completed, including when one or more limits were not met; it does not mean the pilot criteria have been established. Exit status `2` reports invalid arguments, invalid measurements, or unreadable files on standard error and emits no result object.

The operation reads files and writes only to standard output/error. It does not change the inputs, deploy a service, or call a network service. It reads each file once, identifying that snapshot by its digest. Use stable copies when simultaneous measurement updates are possible. Repeating with the same bytes and limits produces the same metrics and checks; paths in the response may differ. Fix the indicated input or access problem before retrying a failed read or validation.

The agent must relate numerical checks to measurement context, applicable criteria, and the work's Outcomes. Successful JSON production cannot establish comparability, the truth of measurement provenance, or suitability beyond the specified pilot.
