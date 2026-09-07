# Conversation recovery evidence

Read [the environment recovery plan](../RECOVERY-ENVIRONMENT-OFFLINE.md) before resuming execution. These supplements preserve original authored text and publicly observed outputs from the existing completed agents' conversations. They are stored separately from the trial files; they neither recreate an execution nor prove current filesystem identity. Each relay states its provenance and missing scope. The evidence branch is not a product branch.

| Original work | Recovered evidence | Available text | Still requires reconciliation |
| --- | --- | --- | --- |
| C069 | [Authored text](control-069-authored-text.md) | Skill and two supporting resources; public execution note | Current original bytes and frozen inventory |
| C070 | [Authored text](control-070-authored-text.md) | Skill and two supporting resources; public execution note | Current original bytes and frozen inventory |
| C071 | [Authored text](control-071-authored-text.md) | Skill and two supporting resources; public execution note | Current original bytes and frozen inventory |
| C072 | [Authored text](control-072-authored-text.md) | Skill and two supporting resources; public execution note | Current original bytes and frozen inventory |
| C-U084 | [Consumer relay](control-use-084-relay.md) | Final answer, note, captured checkpoint JSON | Original bytes/state, uncaptured page responses |
| C-U085 | [Consumer relay](control-use-085-relay.md) | Final answer, note, runner stdout | Checkpoint content was not captured; original state/bytes |
| C-U086 | [Consumer relay](control-use-086-relay.md) | Final answer, note, captured checkpoint JSON and runner output | Original state/bytes and uncaptured artifacts |
| C-U087 | [Consumer relay](control-use-087-relay.md) | Final answer, note with final addition, captured checkpoint JSON | Original state/bytes and uncaptured streams |
| C-U088 | [Consumer relay](control-use-088-relay.md) | Captured answer, final note, captured checkpoint JSON | Original state/bytes and uncaptured artifacts |
| C-U089 | [Consumer relay](control-use-089-relay.md) | Captured answer, final note, captured checkpoint JSON | Original state/bytes, lock and uncaptured artifacts |
| C-U090 | [Consumer relay](control-use-090-relay.md) | Final answer, final note, captured checkpoint JSON | Original state/bytes and durability metadata |
| C-U091 | [Consumer relay](control-use-091-relay.md) | Final answer, note, captured pretty-printed checkpoint JSON | Original compact serialization, state/bytes and lock |
| C-U092 | [Consumer relay](control-use-092-relay.md) | Final answer, final note, exact captured request.json and historical hash/size observations | Actual final API state still needs capture; original state/bytes and lock |
| C-U093 | [Consumer relay](control-use-093-relay.md) | Final answer, note, runner stdout | Workflow SQLite bytes/SQL and journals; original API state/bytes |
| S06-P02 primary | [Assessment report](../grades/business-S06-P02-primary.md), [probe relay](S06-P02-primary-probes-relay.md) | Full finished report, original probe script, all eight observed event objects | Original JSON serialization, two disposable databases/native SQL; independent second review |

The parent verified each delegated immutable tree contains only its assigned UTF-8 recovery blob, checked its path, mode, SHA and byte length, and retained the retrieved content for exact read-back comparison after committing. This verifies preservation of the relay. It does not independently verify all historical claims within the relay or replace the required blind semantic/business reviews.

C-U084–093 completed before disconnection; none was rerun for this recovery. The parent only ended the suspended waiting turns of C-U094–097; their original contexts remain available. Do not turn absence of filesystem access into a completed trial or a fresh retry. See [checkpoint receipts](checkpoint-receipts.md) and the current exact evidence ref before any normal export.
