# Conversion record: statechart

[Conversion guide](../README.md)

## `skills/statechart/SKILL.md`

Title: Statechart. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Support the decision whether a system that moves between states, such as a product flow, a protocol, or a service, behaves right, with a Mermaid statechart drawn from a TLA+ model of the system that TLC has checked and with each bug shown as a path through states. The chart shows how a system moves between states, in the words of the person who reads it. That person, the reader, decides whether the behavior is right.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each rule that the reader agrees to is an INVARIANT of the model as the reader agreed to it, not weakened to make it hold. | Write the spec, first bullet: "Write each rule that the reader agrees to as an INVARIANT. ... If the model has no variable for a rule, add the variable. Never weaken a rule to make it hold." One condition: the model's INVARIANTs state the agreed rules unweakened. |
| Each chart that is shown or handed off comes from the `chart.mmd` of a run of the command on the spec, its config, and the view when one is given. | Run: "Write a TLA+ spec and its config. Then run: <skill dir>/scripts/statechart SPEC.tla [--config FILE] [--view FILE] [--out DIR]"; Pick the chart: "Put your work in a view module, and give it with `--view`."; Show the chart: "Show `chart.mmd` to the user as a `mermaid` code block."; Hand off: "Give each chart and its Mermaid text to the person who must decide."; references/render.md: "Render each `.mmd` file that you show". "comes from" covers an SVG rendered from `chart.mmd` and does not forbid an edit, which upstream does not forbid. Converter's reading (see findings). |
| Each state label says what the reader can see or cares about. | Opening line: "in the words of the person who reads it"; Pick the chart: "Label each state with what the reader can see or cares about ... Keep variable names out of labels." |
| Each step label says the step as the user sees it happen. | Pick the chart: "Write each step label as the user sees it happen ... Do not name the code or the TLA+ action." |
| The view's labels keep each state of a bug path. | Pick the chart, paragraph on arrows: "Keep each state of a bug path, and keep each mark. When a merge changes a `breaks` state to `mayBreak`, it hides where a rule breaks. Do not merge two states that break different rules, because the reader then cannot see which rule breaks where." Stated as a condition on the labels the agent picks, because the chart itself does not show every break on permitted paths ("Rules not checked", a deadlock past a CONSTRAINT, a rule whose path is only in `tlc-RULE.out`). |
| The view's labels keep each mark. | Pick the chart, paragraph on arrows: "Keep each state of a bug path, and keep each mark. When a merge changes a `breaks` state to `mayBreak`, it hides where a rule breaks. Do not merge two states that break different rules, because the reader then cannot see which rule breaks where." |
| The view's labels merge no two states that break different rules. | Pick the chart, paragraph on arrows: "Keep each state of a bug path, and keep each mark. When a merge changes a `breaks` state to `mayBreak`, it hides where a rule breaks. Do not merge two states that break different rules, because the reader then cannot see which rule breaks where." |
| The person who must decide has each chart with its Mermaid text and, for each bug, one line with the rule, the reader's sentence for that rule, and the path as the report numbers it. | Hand off, first paragraph: "Give each chart and its Mermaid text to the person who must decide. Add one line for each bug: the rule, the reader's sentence for that rule, and the path as the report numbers it." |
| The hand-off says what the model leaves out, which steps the chart hides where it hides any, which state breaks which rule where the Legend names two rules on one mark, and gives the command that makes the files again, with a new `--out` folder. | Hand off: "Say what the model leaves out. Give the command that makes the files again, with a new `--out` folder."; Pick the chart, rules for hidden steps: "In the hand-off, say which steps the chart hides."; Read the report, first bullet: "When two rules break, it names both on one mark, so say in the hand-off which state breaks which rule." |
| Where the model describes code, each bug path has a replay against the real code, as a test or a live repro, with one step for each action. | Hand off, second paragraph: "When the model describes code, replay each bug path against the real code, as a test or a live repro, one step for each action." The next sentence ("If a bug does not occur, think that the model is wrong until you show that it is not.") states a stance, not an observable result, and stays only in the Task (see findings). |

Carried from the frontmatter description into the body:

- "a system that moves between states, such as a product flow, a protocol, or a service" (scope of the work; the upstream body names no kind of system; carried into the Purpose)
- "draw it as a Mermaid statechart" (carried into the Purpose as "a Mermaid statechart")
- "to show a bug as a path through states" (carried into the Purpose as "each bug shown as a path through states")
- Not carried: "The report gives the shortest path to each state that breaks a rule." It states no rule for the work. It is a claim about the command's report, and the verified behavior differs from it (see findings). "Use for /statechart" is a discovery trigger and stays in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- The spec and its config must be written before the command runs. Reason: upstream orders them with a word ("Write a TLA+ spec and its config. Then run:").
- The view module must be written before a run that gives it with `--view`. Reason: Run 3 uses the view module that Pick the chart 1 produces.
- Showing the chart and replaying the bug paths must follow the run that writes the `chart.mmd` and the report they use. Reason: both use results only the run produces.
- No listed order: upstream numbered nothing. The order inside Pick the chart 10 ("First return coarser labels ... If the chart is still too busy, return `null` from `step()`") stays in that Task in upstream's words. Pick the chart 10 implies another run after a chart has been seen (Iteration); upstream does not state it as an order and none is added.

State-changing or external effects the work can have, with the condition upstream states:

- Writes the spec, its config, the view module, and the output folder outside the repository. Upstream condition: "Work in a scratch folder outside the repo." No approval is stated. With no `--out`, the command writes `SPEC-chart` beside the spec.
- Installs TLC (tla2tools.jar 1.7.4) and Java (temurin-25) into mise's store over the network, on the first run when `TLA2TOOLS` is unset and mise lacks them. Upstream states it as a fact ("The first run installs TLC and Java with mise and needs the network.") with no approval or condition.
- Installs the npm package `pele@1.9.0` when a chart is rendered (references/render.md: "Install Pele once, outside the repo."). Condition upstream: the user asks for an image, or a chart is too large to read as text. No approval is stated.
- Runs the view module as code with the permissions of the command. Upstream states no condition.
- Replays each bug path against the real code "as a test or a live repro" when the model describes code. A test can add a file to the repository and a live repro can act on a running system. Upstream states no approval or limit for either.

Also: 11 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/statechart/references/tool-use.md`

Added by the conversion. It has no upstream counterpart. Its statements were checked against the script it documents.

## `skills/statechart/references/render.md`

Unchanged from upstream.
