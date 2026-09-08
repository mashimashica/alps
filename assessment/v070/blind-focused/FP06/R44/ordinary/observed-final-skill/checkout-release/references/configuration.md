# Applying configuration

The parent `SKILL.md` is the authoritative release description. This resource connects its Tasks to an existing local environment; it does not redefine the Outcomes.

## Bindings supplied per application

| Binding | Source and use |
| --- | --- |
| Desired environment | Exact release request; bind it to one supplied state file. |
| Environment path | User-supplied directory containing `release_tool.py`. |
| State path | Existing local JSON state file supplied for that environment. Never create substitute business state. |
| Candidate ID | Exact current request; compare to `inspect.candidate.id`. |
| Candidate digest | Supplied request if present, otherwise current inspection; preserve it with the ID and compare before promotion. |
| Operation authorization | Current request and continuing session authorization; determine which reads and mutations are permitted. |
| Request ID | Existing uncertain attempt or unique new logical promotion identity; retain its environment, state, candidate and digest binding in the application record. |

No application values are hardcoded in the Skill. These are agent-held bindings, not an additional file consumed by the CLI. The command accepts `--state`, not `--environment`; a friendly environment name without a confirmed state mapping is insufficient for mutation.

## Responsibility allocation

| Component | Responsibility and information flow |
| --- | --- |
| Agent | Interprets request and authority, binds environment, evaluates exact approval scope, selects permitted operations, reconciles incomplete effects and judges production results. |
| Existing command | Implements qualification, matching approval gate, promotion, recorded idempotency and two separate observations. Returns JSON plus exit status. |
| Local state | Shared source for candidate, service owner, qualification, approval, production and request history. `qualify` and `promote` update their documented fields. Reads are observations of this mutable source. |
| Owner/application provider | Provides authentic approval and environment mapping outside this command interface. The Skill has no approval operation. |
| Runtime | Python 3 and local file access; state-changing access must be authorized. The supplied simulator uses only the Python standard library. |

Qualification records establish an approval basis, and new qualification replaces that basis. Approval is read by the agent and promotion operation. Candidate changes affect both qualification and approval. Production observations describe the revision returned at observation time; any later production change requires reassessing dependent success claims. Request history supports retry reconciliation and does not substitute for current production observations.

## Connection and feasibility

Read the [command contract](command-contract.md) before execution. Use an argument-vector runner if available, otherwise quote each bound shell argument. Resolve application paths explicitly; do not use `eval`, interpolate untrusted values as command syntax, or rely on the Skill's directory as the state directory. Capture stdout, stderr and exit code for each operation. The current interface already exposes all needed processing, so no wrapper, new service, credentials, network connection, package installation or bundled simulator is needed.

The tool's `--help` can establish available operations without reading state. Its source or observed schema must agree with the documented contract before relying on its gates. If the applying version differs, reassess the affected contract and dependent decisions rather than assuming equivalent semantics.

The configuration can perform release work only where the environment mapping, permission and state are available. It cannot produce approval, repair checkout, guarantee availability beyond the sampled observations, or safely coordinate concurrent writers. Missing owner approval is a handoff condition for promotion, not a reason to abandon independent assessment. Evaluation of this package does not itself establish that any release was executed successfully.
