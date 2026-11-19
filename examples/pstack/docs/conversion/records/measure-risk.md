# Conversion record: benchmark-checklist, blast-radius

[Conversion guide](../README.md)

## `skills/benchmark-checklist/SKILL.md`

Title: Benchmark checklist. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Vet a performance number before it is reported or acted on, so that the verdict on it is one that evidence from runs supports, not a guess about the code.

| Outcome | Basis in the upstream text |
| --- | --- |
| Each question is answered with evidence from a run, not a guess about the code, except a question that a quick ballpark skips or whose gap makes the verdict inconclusive. | Intro paragraph 1: "Answer each question with evidence from a run, not a guess about the code." Exceptions from intro paragraph 2: "For a quick ballpark the user asked for, one run is enough. Still check questions 4 and 7, and say that it is one run. Skip the rest unless that run looks wrong." and from Report bullet 3, the ending upstream gives when question 1, 4, or 7 cannot be answered: "Call the verdict inconclusive when you claim a difference but cannot name the limiter, ... or when you could not check questions 4 and 7. Name the gap." |
| The reported verdict and number claim nothing that an answer to a question contradicts. | Before you run anything, bullet 1: "Write down the claim you expect to make, in the words you would ship ... The questions test that sentence." Report bullet 1: "Lead with the verdict: faster, slower, no measurable difference, or inconclusive." What each question says the number does or does not show: question 2 "If you cannot tune it, do not pick a winner from that run."; question 3 "A result past a limit measured something other than the work"; question 5 "A gap smaller than the run-to-run variation is no measurable difference."; question 6 "A helper that takes 1% of a request can make the request at most 1% faster"; question 7 "... produce numbers for work that never happened." No single upstream sentence states this result. See the finding on the faster and slower verdicts. |
| Where a difference is claimed without a named limiter, a side ran untuned, or questions 4 and 7 could not be checked, the verdict is inconclusive and the gap is named. | Report bullet 3: "Call the verdict inconclusive when you claim a difference but cannot name the limiter, when a side ran untuned, or when you could not check questions 4 and 7. Name the gap." Question 2: "If you cannot tune it, do not pick a winner from that run." |
| The reported number has its unit and the run count with it, and outside a quick ballpark also the range and the limiter, unless the limiter is the gap an inconclusive verdict names. | Report bullet 2: "Give the number with its unit, the run count, the range, and the limiter." Question 1: "Name the limiter." Question 5: "Report the median and range." The exceptions follow intro paragraph 2 (a quick ballpark is one run and skips questions 1 and 5, so it has no range and need not have a limiter; its unit and its run count are still available) and Report bullet 3 (a limiter that cannot be named is the gap an inconclusive verdict names). |
| A quick ballpark is reported as one run. | Intro paragraph 2: "For a quick ballpark the user asked for, one run is enough. Still check questions 4 and 7, and say that it is one run." |

Carried from the frontmatter description into the body:

- "before you report or act on it", from the description sentence "Vet a perf measurement (limiter, tuning, limits, errors, repeatability, relevance, and whether the work happened) before you report or act on it." The upstream body says when the skill is used ("when you produce a performance number") but states this timing only for two playbooks (Other perf material). Carried under Constraints as "Vet the measurement before you report or act on it." The parenthetical list is not carried, because each of its seven items is one of the seven questions in the body. The second description sentence ("Use when you run a benchmark or report a speedup or regression you measured.") is a trigger that the body's own "Use this when you produce a performance number: ..." covers. It stays in the frontmatter only.

Order dependencies stated under Constraints, with the reason for each:

- The seven questions are worked in the order listed, unless a Task states otherwise. Reason: upstream numbers them 1 to 7, and profile amendment 15.2 makes the listed order the default for what upstream numbered.
- "The Tasks under Before you run anything come before any run." Reason: upstream's heading says so with the order word "Before".
- No order among the three Tasks under Before you run anything, stated explicitly, because upstream does not number them and states none.
- "Vet the measurement before you report or act on it." Reason: the description states it with "before" (absorbed).
- Under ### Other perf material, in upstream's own bullets: the Perf issue playbook's baseline is vetted "before the playbook plans from it", and the Hillclimb playbook's harness "before it is frozen".
- Orders that concern one question stay inside it: question 1 "find it before you call the change useless", question 2 "Tune it and measure again before you pick a winner".

State-changing or external effects the work can have, with the condition upstream states:

- Running the benchmark, and a separate profiling run (question 1), puts load on the machine and on whatever the load generator targets. Upstream states no approval. Its conditions are on the method: "Profile in a run you do not report", "Run each side at least 5 times, alternating".
- Stopping other work on a busy machine. Upstream implies it ("If the machine is busy, find out what is running. If you cannot stop it, interleave the sides ...") and states no approval or limit on what may be stopped.
- Editing the measurement script: "If the script does not count errors, add the count." Condition: only when the script does not count errors.
- Changing a side's settings: "Tune it and measure again before you pick a winner." Condition: when a limiter is a setting. No approval stated.
- Writing the PR body and a linked artifact or notes file: "Keep a PR body to one primary number. Put the runs, range, and limiter evidence in a linked artifact or notes file." No approval stated.

Also: 7 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/blast-radius/SKILL.md`

Title: Blast radius. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Find what a change breaks somewhere else, before it ships, with the one fact it's safe because of either proven by running real code or marked unproven. Companion to `how` and `why`. `how` tells you what the code does. `why` tells you why it's shaped that way. Blast radius tells you what it breaks somewhere else.

| Outcome | Basis in the upstream text |
| --- | --- |
| The one fact the change is safe because of is stated and is either proven by running the real code, with the proof shown, or marked unproven. | Step 2: "Find the one fact it's safe because of." Step 5: "Prove the one fact. Write a script or test that runs the real code, run it, and paste what happened." What to hand back, bullet 2: "State it, say which step you got it to, and show the proof. If you couldn't prove it, write unproven." Reply: "with the one safety fact either proven or marked unproven". Description: "prove the one fact it's safe because of by running real code instead of writing it up". |
| For each fact the change's safety depends on, the writeup says how far down the How sure are you list it got. | How sure are you: "For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped." What to hand back, bullet 2: "say which step you got it to". |
| The writeup keeps the confirmed risks, each with how likely and how bad, apart from what was checked and cleared. | Step 4: "Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately." What to hand back: "**Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check." and "**Cleared.** What you checked and why it's fine." |
| Every `file:line`, caller, and API the writeup cites is real. | Step 4: "Cite a real `file:line`, a search that finds nothing is still an answer, and never make up a caller or an API." How sure are you, item 2: "A real `file:line`, or the library's own source." After the hand-back list: "cite real code". |
| The risks and the cleared items reach past where grep stops, not only to a list of callers. | Intro paragraph 3: "Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you." Step 3: "Look where grep stops. ... Follow what a symbol search misses". Worded with "not only" because step 4 accepts a search result as an answer ("a search that finds nothing is still an answer") and risks can also come from reading the change (step 1) or the safety fact (step 2). |

Headings whose text changed:

- "## Steps" became "## Tasks". Only element names are allowed as H2 headings, and with one list of steps a single Activity named "Steps" would add no grouping (profile section 5: a plain "## Tasks" list when upstream has a single list). No file cites the heading by name. The governing sentence says the items are cited as steps. setup-pstack is converted the same way.

Order dependencies stated under Constraints, with the reason for each:

- "Task 1 comes first, because every later Task works from what the change does."
- "Task 4 weighs the risks that Tasks 2 and 3 turn up."
- "Task 5 proves the fact that Task 2 finds."
- An order on an effect stays in its sentence under Outputs: "strip anything private before it goes anywhere public".

State-changing or external effects the work can have, with the condition upstream states:

- "Pull the PR and its commits." (step 1) fetches from the remote into the local checkout. Upstream states no approval or limit.
- Writing and running "a script or test that runs the real code" (step 5, and item 4 of How sure are you) creates files in the workspace and executes project code. Upstream states no approval, no location, and no cleanup. The script is handed back ("including the script you wrote").
- "You reproduced it in the running app." (item 5 of How sure are you) drives a running app. The only condition is "as far down this list as is cheap".
- "run it as an `arena`" (step 6) starts runs on more than one model. Condition: "For a big or wide change".
- The writeup going "anywhere public". Condition upstream states: "strip anything private before it goes anywhere public."

Also: 7 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).
