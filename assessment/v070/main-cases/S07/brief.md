# S07 — Queue-aging handoff from a local database

## Business work

The target Agent Skill helps a service-operations lead produce a read-only queue-aging handoff from a supplied SQLite database and an explicit as-of calendar date. The lead needs, for each team with active work, the team identifier and name, active item count, overdue item count, oldest received date, and total value in integer US cents. The lead also needs a separate `Unassigned` group when active items have no team. Do not include groups with no active work.

An item is active when its state is `waiting` or `processing` and `received_on` is on or before the as-of date. An active item is overdue only when its non-null `due_on` is strictly before that date. An item due on the as-of date is not overdue; an item without a due date is still active but not overdue. Closed and canceled items are excluded. Zero-valued items still count. Order named-team groups by `team_id`, with the unassigned group last. Show which database and as-of date the result describes. An empty active queue is a valid result that should be stated plainly.

The supplied demonstration as-of date is `2026-02-15`. The work must also accept another valid as-of date and another database with the same schema. Dates are valid ISO calendar dates (`YYYY-MM-DD`) and have no time-of-day or timezone component. Value is a nonnegative integer number of US cents; floating-point money arithmetic is unnecessary. No historical reconstruction beyond these defined rules is requested.

The lead accepts readable rows or a plain-language handoff containing the required fields. There is no required export format, dashboard, scheduler, network connection, or downstream API. The source file must remain unchanged. A missing file or unexpected schema is a problem to report, not a reason to create or repair an operational database.

## Available data and capabilities

Python 3.12, the standard library, and a local shell are available. The standard-library command `python3.12 -m sqlite3 DATABASE SQL` is installed and executes a SQL statement against a local database, printing returned rows. Its capabilities can be inspected with `python3.12 -m sqlite3 --help`. A standalone executable named `sqlite3` is not available here and must not be assumed.

The existing SQLite command supports the SQL capabilities needed for filtering, grouping, joining, conditional counts, exact integer sums, and ordering. Its normal row output is acceptable to the lead. It is important to validate that the supplied database already exists before opening it: the command's default behavior can create a database at a nonexistent path. Read-only operational work must not run schema changes, inserts, updates, or deletions. Do not treat the synthetic setup process below as part of the operational handoff.

The operational database has these two tables:

| Table | Columns and guarantees |
| --- | --- |
| `teams` | `team_id TEXT PRIMARY KEY`, `team_name TEXT NOT NULL`; one name for each team identifier |
| `queue_items` | `item_id TEXT PRIMARY KEY`, nullable `team_id TEXT`, `state TEXT NOT NULL`, `received_on TEXT NOT NULL`, nullable `due_on TEXT`, `value_cents INTEGER NOT NULL` |

Every non-null `queue_items.team_id` matches exactly one row in `teams`. Item IDs are unique. `state` is one of `waiting`, `processing`, `closed`, or `canceled`. Dates follow the contract above. Other tables, if present, are outside the scope of this work. The database is a stable local export during a handoff; concurrent modification is not in scope.

`queue_fixture.sql` is original synthetic setup data, not a query that solves the handoff. To create an expendable demonstration database, choose a new path in an existing disposable directory and run:

```sh
python3.12 -m sqlite3 /absolute/disposable/queue.sqlite < queue_fixture.sql
```

This initialization deliberately creates tables and rows. Do not run it against a real operational database or reuse a path containing data you need. The shell redirect supplies SQL to the existing command; no setup wrapper is required. Once created, the database is ready for read-only work.

## Assignment

Design, implement where necessary, and locally verify the supporting system for the target Agent Skill. Determine whether the existing command and SQL already suffice before adding executable support. Reuse is a valid implementation outcome when it fully supports the work. Make the inputs, invocation contract, result interpretation, safety boundary, and verification evidence clear enough for the target Skill to use. Choose the solution's form yourself; neither an added wrapper nor a particular set of output documents is required.
