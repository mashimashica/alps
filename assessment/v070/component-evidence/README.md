# Preserved component evidence

These are original independent grader probe sources/results and native snapshots
of their disposable states. They are not additional creator/consumer trials or
ALPS distribution resources. Each preservation.json records the original path,
representation and hash. Original workspaces were not changed or deleted.

| Preserved folder | Original workspace | Assessment |
| --- | --- | --- |
| dev1-S08-primary | ../s08-grade-probes-R7GDu8 | grades/dev1-S08.md |
| dev1-S08-second | ../s08-second-probes-bIw1At | grades/dev1-S08-second.md |

Python and JSON files retain their original text bytes, including the second
review's exact main-probe argv/exit/stdout/stderr results. SQLite files are
represented by consistent native SQL snapshots of committed logical state,
not original database bytes. The second review's supplementary observations are
in its public report; no separate full supplementary result transcript was
present in that workspace. Probe scripts retain original absolute paths and
must be reviewed and explicitly bound to a new disposable environment if run
again; a rerun cannot recreate the original concurrency schedule.
