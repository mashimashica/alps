# Release tool interface

The supplied executable is invoked as:

```text
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

Operations:

| Operation | Effect and interpretation |
|---|---|
| `inspect` | Reads and prints the complete state. It does not mutate state. |
| `qualify --candidate ID` | Checks the current candidate ID, writes qualification evidence containing its current digest and a new sequence, and exits nonzero when `qualification_ok` is false. It does not approve. |
| `promote --candidate ID --request-id ID` | Changes production only when qualification and later owner approval match candidate and digest. A repeated matching request ID returns the prior result without another promotion. |
| `request-status --request-id ID` | Reads the recorded result for a promotion request; use after timeout or other uncertain effect. |
| `probe` | Reports production revision and `healthy`; exit 0 only when healthy is true. |
| `checkout` | Reports production revision and `checkout_ok`; exit 0 only when checkout works. |

JSON output is the evidence record. A nonzero exit code means the requested condition was not established; inspect the JSON for the reason. Promotion can return a timeout after changing state, so status and state inspection are required before retrying.
