# S05 second grader — preserved component-probe evidence

This is a post hoc preservation of an already performed narrow component probe. No behavioral test was rerun while assembling this record, and no evaluated package was changed.

## Provenance and file types

- `probe-command.transcribed.txt` is an exact transcription of the public shell command submitted in the original tool call, including the complete Python harness and its original synthetic fixture literal.
- `probe-stdout.transcribed.txt` is an exact transcription of the tool-visible harness output. It is not an original log file.
- `probe-fixture.transcribed.json` preserves the same three-line fixture value in readable JSON. The original temporary input file was not retained. Its original serialization was Python `json.dumps(d)` with no appended newline; this readable transcription is not claimed byte-identical to that temporary file.
- `posthoc-source-hashes.json` and `posthoc-source/` preserve subsequently read, unchanged package-source bytes and their SHA-256 hashes. These are post hoc source snapshots, not recovered original temporary copies.

No original probe command file, stdout file or copied script file was saved during the run. The original public tool call remains the basis of the command/output transcriptions. No private reasoning is included.

## Disposable location and missing trace

The exact temporary-directory pathname was not printed or retained. The harness requested `tempfile.TemporaryDirectory(prefix='s05-second-conflict-probe-')`; its conceptual path was `<tempfile.gettempdir()>/s05-second-conflict-probe-<unrecorded suffix>`. Neither the resolved temporary root nor the suffix is asserted here. Within it the files were `input.json`, `R17.py`, `R28.py`, `R44.py` and `R63.py`.

Each script was created by `shutil.copyfile(src, dst)` from the specified evaluated package. The harness contains no copied-script editing operation. The context manager removed these temporary files after the probe. Their SHA-256 hashes were not measured contemporaneously and cannot now be directly attested. The preserved post hoc hashes identify the available package-source bytes; they also identify the expected copy bytes conditional on those sources being unchanged since the probe. No grader mutation of those sources occurred. This conditional correspondence must not be described as a recovered hash of an original disposable copy.

The exact resolved `sys.executable` path, temporary-file metadata, start/end timestamps, and full raw per-script JSON stdout were not retained. The harness captured each subprocess's raw stdout in memory, parsed it, and printed only the line/status/flag projection in the preserved output.

## Invocation and captured results

The enclosing tool used `tools.exec_command` with the exact command preserved in `probe-command.transcribed.txt` and `max_output_tokens: 2500`, with no working-directory override. Its code-mode wrapper forwarded `r.output` only and displayed `Script completed`. It did not forward the enclosing shell's numeric exit code or preserve a separately identified aggregate stderr stream. Those aggregate details are therefore missing, not inferred.

The four copied-script subprocesses have explicit captured results in the preserved harness stdout:

| Copy | Subprocess exit code | Captured subprocess stderr | Observed conflict flags |
|---|---:|---|---|
| R17.py | 0 | Empty string | B/Z only; A/X remains a complete shortfall |
| R28.py | 0 | Empty string | A/X only; B/Z remains a shortfall |
| R44.py | 0 | Empty string | A/X only; B/Z remains a shortfall |
| R63.py | 0 | Empty string | A/X, A/SOUND and B/Z |

The original fixture has two distinct contents for event ID CONFLICT, on A/X (+4) and B/Z (+6), plus independent event CLEAN (+5) on complete A/SOUND. Only A/X and B/Z are identified by the conflict. All three lines have explicit complete July coverage. This fixture isolates the specific conflict-propagation discrepancy already visible in the application evidence. It is not either business receiving packet, an outcome-improving retry, or a candidate repair.

## Post hoc preservation operations

The preservation step read the four package script files and computed SHA-256 with Python `hashlib.sha256(p.read_bytes()).hexdigest()`. That separate read-only command returned exit code 0; its exact command and captured stdout are preserved in `posthoc-hash-command.transcribed.txt` and `posthoc-hash-stdout.transcribed.txt`. Copies in `posthoc-source/` were subsequently written with `apply_patch` and checked for byte equality with those same package files. No script was executed in this preservation step.
