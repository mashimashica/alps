# Verification evidence and limits

Locally verified using Python 3.12, the supplied immutable-ledger CLI and original 17-entry fixture. The isolated test harness, outside this reusable Skill, passed eight tests. It created temporary source states and granted further tranches only as simulated operator actions; the operational runner contains no grant or initialization calls.

Verified behaviors:

- Full fixture traversal examines 6, 12, then 17 records across three tranches. Re-running at exhausted quota preserves checkpoint contents. Re-running a completed request consumes no page calls.
- Fixture vendor results retain Cedar's zero net and Dune's negative net, include both date boundaries, and exclude pending, void and out-of-interval entries.
- Reversed, impossible and noncanonical dates fail with no checkpoint and no consumed calls.
- Empty ledger returns a complete empty result after one terminal page; a no-match interval still traverses all six fixture pages.
- A test adapter discards the first successful page response after source quota is charged. The checkpoint remains unadvanced, retry uses the remaining call, and completion needs four tranches with no doubled entries.
- Changed interval and malformed checkpoint fail without consuming page quota.
- Nonchronological records after nonqualifying records, a zero-valued qualifying entry, and an amount of `10**40` cents produce the expected exact results.
- Direct protocol checks reject wrong snapshots, premature terminal markers, missing terminal markers, duplicate entries, floating amounts, empty nonterminal pages and re-incorporation of a saved cursor before mutating the checkpoint.

The runner's `--help`, required Skill frontmatter, matching folder name, Python syntax and local Markdown resource links were also checked.

Verification limits: tests used the local simulator, not a production API. The lost-response test simulates one specific response-loss window; exhaustive process-kill, filesystem failure/power-loss, lock contention, timeout, every API error combination and concurrent operator-grant races were not exercised. Atomic checkpoint saving and locking rely on documented POSIX filesystem semantics. The operator must serialize grants with execution. Checkpoints are trusted internal state; validation detects structural and identity inconsistencies but cannot establish authenticity after deliberate editing. Runtime memory/storage scalability was not benchmarked. The official reference Skill validator was not run; the local format check covers only the required metadata and links.
