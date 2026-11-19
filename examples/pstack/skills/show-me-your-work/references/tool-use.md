# Tool use for log.sh

Paths in this file are relative to the skill folder.

## Responsibility and limits

`scripts/log.sh` appends one row to a tab-separated decision log. It creates the log's parent directory when that is missing, writes the header line when the file is missing or empty, stamps the `ts` cell with the current UTC time, and cleans the five cells it is given.

- It only appends. It does not read, check, edit, or delete rows.
- The header is always `ts`, `phase`, `decision`, `why`, `evidence`, `result`, separated by tabs. `references/decision-log-template.tsv` holds the same line. The script does not read that file.
- A file that already has content is appended to as it is. Its header and its column count are not checked.
- When the existing file does not end with a newline, the new row is joined to its last line.
- Cleaning replaces each tab, line feed, and carriage return in a cell with one space. It then puts a single quote in front of a cell whose first character is `=`, `+`, `-`, or `@`. The quote is stored in the cell, so `-1 regression` is stored as `'-1 regression`. Nothing else is changed. A cell that starts with a space followed by `=` gets no quote. Double quotes and other control characters pass through.
- The log path and the `ts` cell are not cleaned.
- A log path that starts with `-` is passed to `dirname` as an option. `-dash.tsv` fails with exit status 1 and writes nothing. `-`, `--version`, and `--help` exit 0 and write the log at that name in the working directory. `--version` and `--help` also create directories named from the text `dirname` prints.
- The script takes no lock. The test for a missing or empty file and the writes are separate steps, so a stray second header line is possible when callers race or when the test misreports an existing log. Rows are appended either way.
- It does not write `start` rows, check that evidence resolves, or stop anyone from editing earlier rows.

## Invocation

```
scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

The script needs bash and has the executable bit set. Run it directly or through `bash`. Where `sh` is dash, `sh scripts/log.sh` fails.

- It takes exactly six arguments. It has no flags, reads nothing from stdin, and reads no environment variable of its own. `--help` counts as a wrong argument count.
- `logfile` is the path of the log. A relative path resolves against the caller's working directory, not the skill folder. A symlink is followed.
- `phase`, `decision`, `why`, `evidence`, and `result` are the text of columns 2 to 6. Pass each as one shell word. An empty string gives an empty cell.
- `ts`, column 1, is not an argument. It is the time of the append from `date -u +%Y-%m-%dT%H:%M:%SZ`. It is UTC whatever `TZ` holds, and it has one-second resolution.

## Returned information

The script prints nothing on stdout, on success or on failure. A wrong argument count prints `usage: log.sh <logfile> <phase> <decision> <why> <evidence> <result>` on stderr. Other failures print the error text of bash or of the failing command on stderr.

| Exit status | Meaning |
| --- | --- |
| 0 | A row was appended. |
| 1 | The argument count was not six, or a step failed. The failures checked were a log path that is a directory or is empty, a log path such as `-dash.tsv` that `dirname` rejects as an option, a parent path component that is a file, and a failed write. |
| 127 | `dirname` or `date` was not found, or `mkdir` was not found when the parent directory was missing. |
| 2 | The script was run through `sh` where `sh` is dash. |

Exit status 1 covers both a usage error and an I/O error. The stderr text tells them apart.

## Dependencies and environment

- bash, found through `/usr/bin/env`.
- `dirname`, `tr`, and `date` with `-u` and a `+` format. `mkdir` is needed only when the parent directory is missing.
- Write permission on the log file and its directory.
- No network, no credentials, and no other file of the plugin.

The script declares no versions. The behavior in this file was checked on Linux with bash 5.2 and GNU coreutils 9.4. macOS and network mounts were not checked.

## Success, failure, and incomplete results

- Success is exit status 0 with the new row as the last line of the file, in six tab-separated fields.
- A wrong argument count fails before anything is written. No file or directory is created.
- A failure can leave part of the work done. With `date` missing the header is written, no row follows, and the status is 127. A parent directory can be created before a later step fails.
- Exit status 0 can come with a bad row. With `tr` missing the script appends a row whose five cells are empty, prints `tr: command not found` on stderr, and still exits 0.
- Exit status 0 also covers a row joined to an unterminated last line, and a six-field row under a header with other columns.

Read stderr as well as the exit status. When either leaves doubt, read the last line of the file.

## Effects on external state

A call changes files in the caller's environment and nothing else. It can do these things, in this order:

1. Create the missing parent directories of the log path, or, for a log path that starts with `-`, the directories described under Responsibility and limits.
2. Create the log file when it is absent.
3. Append the header line when the file is absent or empty.
4. Append one row.

Every write appends. The script never truncates or rewrites existing content, and it cannot correct a row once written.

The call is not idempotent. Repeating it appends a second row, and two rows written within the same second carry the same `ts`.

- After a nonzero exit status no row was written in the cases checked. A header-only file does no harm, because the next call finds content and skips the header. Retrying after the cause is fixed adds no duplicate in those cases.
- After an uncertain result, such as a killed process or exit status 0 with errors on stderr, read the last line of the file before retrying.

## Reproducibility

Columns 2 to 6 depend only on the arguments, and the header is constant. Column 1 comes from the system clock and cannot be supplied or frozen. Two calls with the same arguments therefore differ only in `ts`. Rows keep append order. `ts` does not order or identify rows written within the same second.

## What a result does not establish

Exit status 0 establishes that a line was appended. It does not establish any of these:

- The cells hold the text that was passed. A missing `tr` empties them, and cleaning changes whitespace and adds the quote prefix.
- The row sits on a line of its own under a matching header.
- The evidence resolves or shows what the row claims.
- The row records a real decision, or follows the `start` row convention.
- Earlier rows were left unedited.
