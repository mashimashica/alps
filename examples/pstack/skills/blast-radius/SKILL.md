---
name: blast-radius
description: "Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running real code instead of writing it up. Use for 'blast radius of X', 'what could this break', or reviewing a small diff you don't trust."
disable-model-invocation: true
---

# Blast radius

## Purpose

Find what a change breaks somewhere else, before it ships, with the one fact it's safe because of either proven by running real code or marked unproven. Companion to `how` and `why`. `how` tells you what the code does. `why` tells you why it's shaped that way. Blast radius tells you what it breaks somewhere else.

## Outcomes

- The one fact the change is safe because of is stated and is either proven by running the real code, with the proof shown, or marked unproven.
- For each fact the change's safety depends on, the writeup says how far down the How sure are you list it got.
- The writeup keeps the confirmed risks, each with how likely and how bad, apart from what was checked and cleared.
- Every `file:line`, caller, and API the writeup cites is real.
- The risks and the cleared items come from looking where grep stops, not from a list of callers.

## Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. Pull the PR and its commits.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run: microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. Be honest about each risk. Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately. Cite a real `file:line`, a search that finds nothing is still an answer, and never make up a caller or an API.
5. Prove the one fact. Write a script or test that runs the real code, run it, and paste what happened.
6. For a big or wide change, run it as an `arena`. Ask more than one model the same question and merge the answers. Different models catch different real bugs.

## Outputs

### What to hand back

- **What it does.** What changed, including the part that isn't obvious.
- **The one fact it's safe because of.** State it, say which step you got it to, and show the proof. If you couldn't prove it, write unproven.
- **Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.

Write it through `unslop`, cite real code, and strip anything private before it goes anywhere public.

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.

## Controls

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

### Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

#### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you're worried about.

## Constraints

Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Task 1 comes first, because every later Task works from what the change does.
- Task 4 weighs the risks that Tasks 2 and 3 turn up.
- Task 5 proves the fact that Task 2 finds.
