# Working example: assessing a service change

[Japanese translation](locales/ja/README.md)

This informative example is a complete target Skill with a working script. It is bundled as reference material under `examples/`, outside the Plugin's discovered `skills/` directory. Read [Service Change Assessment](assess-service-change/SKILL.md) for the work's Name, Purpose, Outcomes, and conditions. That description is the common source for both design responsibilities below.

## Two design responsibilities on the same work

| Responsibility | What it clarifies in this example | Evaluation subject |
| --- | --- | --- |
| [Process Description Design](../skills/design-process-description/SKILL.md) | Observable assessment results, the boundary with deployment, applicable pilot criteria, necessary Activities and Tasks, and the roles of measurements and capabilities. | The meaning and relationships in the [target description](assess-service-change/SKILL.md). |
| [Agent Work System Design](../skills/design-agent-work-system/SKILL.md) | How an agent, local Python tool, measurements, and pilot context interact; which work is calculated and which needs contextual judgment. | The supporting configuration, its implementation, and evidence of effective assessment. |

## Configuration and interfaces

| Part | Responsibility and interaction |
| --- | --- |
| Agent | Identifies the work description and applicable context, selects measurements and limits, invokes the calculation, assesses comparability, and justifies the resulting decision or identifies missing evidence. It can propose additional measurements or a changed method within the request. |
| [Measurement tool](assess-service-change/scripts/compare_measurements.py) | Performs the settled sequence of CSV validation, aggregation, and numerical comparisons as one public operation. Internal functions separate input validation and CLI coordination. |
| Measurement files | Inputs examined by the work. Their paths are tool arguments; their contents and provenance carry the evidence. The response identifies the bytes used with SHA-256 digests. |
| [Pilot conditions](assess-service-change/references/pilot-context.md) | Controls for the applicable criteria and Input for examining measurement comparability, distinguished by those roles. Numerical limits become explicit tool arguments. |
| Local environment | An agent with file-reading and command capabilities, Python 3.11 or later, and stable readable files. The script needs no network or third-party packages. |

The script is an Enabler when used in the assessment and an Output of the work that implements this configuration. One invocation supports calculation and interpretation Tasks; it cannot establish every condition those Tasks assess. Its JSON return is calculation evidence used by the agent, while the assessment's result also depends on measurement context. The agent can provide the judgment in the user's requested medium; no fixed report file is required.

## Run the processing operation

From `examples/assess-service-change/`:

```console
python3 scripts/compare_measurements.py assets/baseline.csv assets/candidate.csv --min-samples 4 --max-p95-ms 200 --max-error-rate 0.05 --max-p95-increase-ms 50
```

See [tool use](assess-service-change/references/tool-use.md) for data meanings, dependencies, invocation, failure handling, and reproducibility conditions. The supplied fixture produces baseline p95 **130 ms**, candidate p95 **160 ms**, an increase of **30 ms**, and candidate error proportion **0**. All numerical comparisons hold. A positive pilot assessment also needs the [specified context](assess-service-change/references/pilot-context.md) to apply.

## Evaluation cases

The table gives criteria for evaluating the example, not a claim that every agent or environment has been tested.

| Level | Case and evidence | Required interpretation |
| --- | --- | --- |
| Description | Review the target description against the Framework, its pilot conditions, and the system design. | Assessment, deployment, numerical results, and the evidence needed for each Outcome remain distinguishable. |
| Tool and connections | Run the documented CLI on the supplied pair; parse the returned object and compare its metrics with the inspectable fixture. | Values and comparisons match the specified calculations, input identity is traceable, and the command can be consumed through the agent's existing command tool. |
| Tool failure | Supply a missing file, malformed row, duplicate identifier, invalid status, or non-finite duration. | Exit `2`, a diagnostic, and no result object; obtain valid evidence before a dependent assessment. |
| Work system | Use the supplied pair and its applicable context. | A positive judgment is supported for this synthetic pilot only, with the small sample and production limits stated. |
| Work system | In a copy of the candidate, change its last request to `c4,2000,error`, preserving the specified measurement context for this test case. | The tool still exits `0`, but candidate p95 is 2000 ms, error proportion is 0.25, and p95 increase is 1870 ms. The agent must give a negative pilot assessment. A completed calculation has not made the candidate acceptable. |
| Work system | Supply the normal measurements but state that the candidate used ten concurrent clients instead of one. | Numerical checks still hold, but comparable conditions have not been established. The affected assessment Outcome remains unconfirmed. Identify the additional evidence needed. |

Repository tests exercise the script and CLI contract. An agent-mediated application of these cases is needed to evaluate the whole configuration. Record the actual agent/environment, cases, judgments, and limits when reporting that evaluation. Fixture calculations do not validate an operational service or the scientific adequacy of a production measurement plan.
