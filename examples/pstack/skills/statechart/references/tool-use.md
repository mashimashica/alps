# The statechart command

`scripts/statechart` is the command that `SKILL.md` tells you to run. This page gives its interface, its results, and its limits. `SKILL.md` says how to write the spec and the view, and how to read the chart and the report.

## Responsibility and limits

The command has one operation. It reads a TLA+ spec, a TLC config, and a view module when you give one. It runs SANY on the spec. Then it runs TLC to decide each INVARIANT and each PROPERTY, and deadlock unless the config says `CHECK_DEADLOCK FALSE`. It writes a report, and a Mermaid chart when it has one, to an output folder.

The command does not render an image. It never changes the spec, the config, or the view. It has these limits:

- The only options are `--config`, `--view`, and `--out`. There is no `--help` and no `--version`.
- No run has a time limit, and the first TLC run has no bound on its states. To stop a run, send SIGINT or SIGTERM to the command.
- After a rule breaks, a rerun stops at 100,000 distinct states only while no TLC run has explored the whole state space. After a run has explored it, the reruns have no bound.
- The count that the command holds against the chart budget of 500 is the largest count of distinct states from any of its TLC runs. The reruns without the rules that break count too. So a model with more than 500 states gets only the bug paths, also when the run on the config as written stops at a break before it reaches 500 states.
- The report gives one path for each rule that breaks. It is a shortest path to a state that breaks the rule. The other states that break the rule get no path. For a PROPERTY, the path is TLC's counterexample.
- In a chart without regions, the chart draws a step on a bug path that stays in one chart state, as an arrow from that state to itself.
- The command reads the config itself before TLC does. It reads only these section keywords: `CONSTANT`, `CONSTANTS`, `CHECK_DEADLOCK`, `INIT`, `NEXT`, `SPECIFICATION`, `VIEW`, `SYMMETRY`, `TYPE`, `TYPE_CONSTRAINT`, `INVARIANT`, `INVARIANTS`, `PROPERTY`, `PROPERTIES`, `CONSTRAINT`, `CONSTRAINTS`, `ACTION_CONSTRAINT`, and `ACTION_CONSTRAINTS`. Any other word where a section keyword must stand stops the command before TLC runs, `ALIAS` too. It also stops, before TLC runs, on a config that it finds TLC would refuse or would read in another way than the config is written.
- The module name is the name of the spec file without `.tla`. The command finds the modules that the spec uses only in the folder of the spec and in `tla2tools.jar`.
- The command adds modules named `ChartBound` and `ChartRun` that extend the spec. They define `ChartTLC`, `ChartNaturals`, `ChartBound`, `ChartBudget`, `ChartBroken`, and `ChartMark`. A spec that defines one of these names clashes with them. The command does not look for the clash.
- The view is code. The command imports it and runs it with the permissions of the command.

## Invocation

```sh
<skill dir>/scripts/statechart SPEC.tla [--config FILE] [--view FILE] [--out DIR]
```

| Argument | Meaning | Default |
| --- | --- | --- |
| `SPEC.tla` | The TLA+ module to check. Give exactly one. | None. |
| `--config FILE` | The TLC config. | `SPEC.cfg` beside the spec. |
| `--view FILE` | The view module. | Each state shows its values, and each step shows its TLC action name. |
| `--out DIR` | The output folder. It must not exist yet, or it must be empty. A hidden file makes it not empty. | `SPEC-chart` beside the spec. |

`scripts/statechart` is a `/bin/sh` script. It runs `statechart.ts` beside it on the first runtime that fits, in this order:

1. Node 22.18 to 22.x, or Node 23.6 or later.
2. Bun 1.1.5 or later.
3. Deno 2.0 or later.

With none of them, it prints what it needs and exits 127.

The command reads these environment variables:

- `TLA2TOOLS` is the path of `tla2tools.jar`. When it is set, the command does not call mise.
- `JAVA` is the Java binary. Without it, the command uses `java` on `PATH` when `TLA2TOOLS` is set, and the Java that mise installs otherwise.
- `TMPDIR` is where the command makes its temp folder.

The command does not check `TLA2TOOLS` or `JAVA` before it uses them. It reads no standard input and asks nothing.

The view has these rules:

- It can export only `state`, `step`, `group`, `colors`, and `title`. Any other export stops the command, a default export too.
- `colors` is a plain object. Each value is `blue`, `orange`, `purple`, `yellow`, `teal`, `tan`, or `pink`. A view that exports `group` must export `colors`, and `group()` returns `undefined` or a name in `colors`.
- `state()` returns the same regions, in the same order, for every state. A state cannot also be the parent of another state.
- A label is a string that is not empty. It cannot hold the word `undefined`, the word `NaN`, or the text `[object Object]`.
- `step()` returns a label or `null`. The command stops when `step()` returns `null` for a step on a bug path, or for a step that leaves the loop of a PROPERTY counterexample.
- In `vars`, a model value is a string of its name, so it looks the same as a string. An interval is an array. A record or a function is an object with the text of each key as a key.
- What the view prints to standard output lands in the standard output of the command.

## Returned information

On exit 0 or 1, standard output holds the text of `report.md`, an empty line, and `Wrote DIR`. It does not hold the chart. On any other exit, standard error usually says why. An argument error adds the usage text.

On exit 0 or 1, the output folder holds these files:

- `report.md`, always.
- `chart.mmd`, when the command has a chart.
- `tlc.out`, always.
- `tlc-RULE.out`, for each PROPERTY that breaks, and for each other rule that breaks with no path in the report.

`report.md` has these parts, in this order:

1. The title `# MODULE`.
2. One line with the counts of states and steps, or with the chart budget.
3. Lines that say how the chart differs from the model. The section on incomplete results lists them.
4. One section `## RULE breaks` for each rule that breaks. With a path, it has the line `The shortest path has N steps:` for an INVARIANT or deadlock, or `TLC's counterexample is in tlc-RULE.out. It has N steps:` for a PROPERTY. Then it has the numbered lines of the path, `0. STATE` and then `1. STEP: STATE`. The path of a PROPERTY can end with a line that names the states that the run repeats forever. With no path, the section has the line `TLC found a counterexample. It is in tlc-RULE.out.`
5. The sections `## Rules that hold` and `## Rules not checked`, each when it has a rule.

`tlc.out` and `tlc-RULE.out` are plain-text copies of TLC's `-tool` messages. TLC ran in a temp folder, with the flags `-workers 1 -fp 0 -lncheck final`, on a config that the command wrote from the one you gave. What Java printed to standard error comes after TLC's output, so a line such as `Picked up JAVA_TOOL_OPTIONS` can end the file.

## Dependencies and environment

- A POSIX system with `/bin/sh`, `readlink`, `dirname`, `sed`, `kill`, and `rm`.
- One of the runtimes above. The command needs no npm package to run.
- `tla2tools.jar` and Java. The command gets them in one of two ways:
    - With `TLA2TOOLS` set, it uses that jar, and `JAVA` or `java` on `PATH`. Its own message asks for Java 11 or later. It installs nothing and does not use the network.
    - Without `TLA2TOOLS`, `mise` must be on `PATH` already. The command does not install mise. It asks mise for `tla2tools.jar` 1.7.4 and for `java@temurin-25`. When mise lacks one of them, the command runs `mise install` for both. That install needs the network. The command gives mise the URL `https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar` and a sha256 for the jar.
- Write access to `TMPDIR`, to the folder that will hold the output folder, and to the store of mise when mise installs.

Each run starts Java once for SANY, twice when SANY cannot read the spec, and once for each TLC run. TLC runs once on the config as written, again after each break while rules are left to check, and once more for the chart unless a run has already counted more than 500 states.

The command reads TLC's `-tool` messages. It does not check the version of the jar that `TLA2TOOLS` names.

The command does not call Pele. Rendering a chart is a separate step, in `render.md`.

## Success, failure, and incomplete results

| Exit status | Meaning | Output folder |
| --- | --- | --- |
| 0 | In the first TLC run, every rule of the config holds. | Written. |
| 1 | In the first TLC run, a rule breaks. This is a result, not a failure of the command. | Written. |
| 2 | The command has no result. Standard error usually says why. | Not written. |
| 130 or 143 | SIGINT or SIGTERM stopped the command. | Not written. |
| 127 | The launcher found no runtime that fits. | Not written. |

Exit 2 has these causes:

- An argument is wrong, such as two specs or an unknown option.
- The config file does not exist.
- The output folder is not empty, cannot be used, or gets a file while the check runs.
- The view breaks one of its rules, or it throws. The command finds some of these only after TLC has run.
- The command or TLC refuses the config.
- The command cannot find TLC. The message starts with `Cannot find TLC: mise install failed`.
- SANY cannot read the spec. The message starts with `SANY could not read`. A wrong `TLA2TOOLS` or `JAVA` gives the same message, so it does not always mean that the spec is wrong.
- The first TLC run stops on an error, or the run for the chart writes no graph. The message starts with `TLC could not check`.
- TLC prints something that the command cannot read.
- A signal kills the check.
- The check ends before it writes its files, for example when the view ends the process. Standard error can then be empty.

Exit 0 and exit 1 tell only what the first TLC run found. The report says whether the result is whole. These lines in the report mark a result that is not whole:

- `## Rules not checked` comes only with exit 1. The line `TLC stopped with exit N before it checked` under it means that a rerun stopped on an error of TLC.
- `TLC stopped the drawing run with exit N, so the chart draws only the states that it reached before it stopped.` comes with exit 0 or 1. The chart is not whole, and it can be empty. For example, a spec with an INVARIANT named `ChartMark` that holds gives this line, exit 0, and an empty chart.
- A line with `the chart budget of 500` means that the chart draws only the bug paths, or that there is no `chart.mmd`. A missing `chart.mmd` after exit 0 is this case, not an error.
- `TLC checked P only in the initial states, because it has no [], <>, or ~>.` means that `P` is under `## Rules that hold`, but TLC did not check it in every state.
- `TLC found a counterexample. It is in tlc-RULE.out.` means that the rule breaks, and that the report and the chart do not have its path.
- A line that ends with `So the chart draws parent states in place of regions.` means that a regions chart could not show the moves of the model as they are. The line starts with the reason.
- `The chart does not draw N steps that stay in one chart state.` and `The view hides N steps, so the chart does not draw them.` give the counts of the steps that the chart leaves out. The first count does not include a step that the chart draws as an arrow from a state to itself.

After exit 2, 127, 130, or 143 the command wrote nothing. Fix the cause and run the same command again, with the same `--out` folder. After exit 0 or 1 the output folder exists, and the command refuses it. Run again with a new `--out` folder. The command has no option to write over a folder.

## Effects on external state

- The output folder. The command writes every file to a hidden folder first and then moves that folder into place with one rename. So the output folder is whole or absent. The command makes the parent folders that are missing. It never writes over or deletes an output folder. With no `--out`, the output folder is `SPEC-chart` beside the spec.
- Temp folders. During a run the command keeps a folder named `.NAME.statechart-XXXXXX`, where `NAME` is the name of the output folder, and a folder named `statechart-XXXXXX` in `TMPDIR`. The first one is beside the output folder, or in the nearest folder above it that exists. The command removes both when it ends, after a failure or a signal too. A helper process removes them when the command itself is killed. TLC works in the temp folder, so the command writes nothing in the folder of the spec, unless the output folder is there.
- The store of mise. When mise installs Java and the jar, they stay installed for later runs. The command asks mise for both on every run, and it runs the install again when mise lacks one.
- Processes. The command starts the check in a process group of its own and kills that group when it ends.
- The network. The command uses it only through `mise install`.
- The view. It runs as code, so it can have effects of its own.

## Reproducibility

- Every TLC run has the flags `-workers 1 -fp 0 -lncheck final`.
- The same spec, modules, config, view, and jar give the same `report.md` and `chart.mmd`. That needs view functions that depend only on their arguments, and a spec that uses no random operator of TLC. The command does not set TLC's seed.
- `tlc.out` and `tlc-RULE.out` differ from run to run. They hold the seed, times, a process id, a description of the machine, and absolute paths, and they can hold the Java settings of the machine. So they can show these details to a person who gets them.
- With mise, the jar has a pinned version and sha256. With `TLA2TOOLS`, the jar is the one you name.

## What a result does not establish

- Exit 0 says that TLC found no rule of the config that breaks in the model, within its constants and its constraints. It says nothing about a rule that the config does not list, and nothing about the system that the model describes.
- Exit 0 does not say that the chart is whole. The lines above say when it is not.
- Exit 1 does not say that the command failed.
- A rule under `## Rules that hold` can be a PROPERTY that TLC checked only in the initial states.
- A path in the report shows one way to break its rule. Other states can break the same rule.
- `Wrote DIR` says that the files exist. It does not say that the result is whole.
