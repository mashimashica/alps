---
name: ketchup
description: "Catch the user up on what changed in this chat since their last message, in plain words and small visuals. List every item waiting on them with what they need to decide it from the reply alone. Use for /ketchup."
disable-model-invocation: true
---

# Ketchup

## Purpose

Catch the user up on what changed in this chat since the last message they wrote before `/ketchup`, so that they understand each change, not only where it stands, and can make every call waiting on them from the reply alone. Notifications and subagent results are not their messages.

## Outcomes

- The reply tells what came of each thing the user asked for, and whether it is done, still running, failed, or not checked, or it says that nothing happened and nothing waits on the user.
- The reply lists every action item still waiting on the user, even one raised before their last message, and no call made up to fill it.
- The reply alone is enough to decide each call, with "unknown" written for a fact the call needs that is not known.
- Every state, number, and picture in the reply matches the facts it comes from, which for a PR, CI run, or agent this chat touched means its current state.
- Every fact in the reply makes sense, in plain words, to a user who remembers their last message and nothing after it.
- Each visible change has its screenshot or video embedded inline, or its summary line is marked "No screenshot yet," and says what changed on screen.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order.

### Gather what changed

1. Collect your own work since that message, reports from subagents, and messages from anyone else in this chat.
2. Check the current state of each PR, CI run, or agent this chat touched.
3. Check each number you will show against the facts it comes from, and say so when you correct one.
4. One call can cover many items, such as each PR in a set awaiting merge. For each item, collect its link, what it changes for users, the evidence behind your pick, its risk, and your pick. Write "unknown" for a fact the call needs that you do not know. Leave out a link you do not have.

## Outputs

### Write the reply

Spend words on the calls, not on the story. Keep what happened under 100 words, not counting pictures, and shorter when less happened. Leave out work that changed nothing for the user. Give each item about 30 words. The reply grows with the number of items: two items need well under 150 words in all, not counting pictures, and thirty need far more. Never cut items or shrink them to stay under a word count: no count in place of a list, and no link in place of an item. A link can add depth, but the reply alone must be enough to decide.

Open with one short sentence that names what waits on the user, or says nothing does. The action items give the detail. If nothing happened and nothing waits on the user, say so and stop.

Then show what happened, pictures first. Embed inline the screenshots and videos the work produced, then any diagram that explains a change. Then sum up in one short bullet per thing the user asked for: what came of it, and whether it is done, still running, failed, or not checked. Write each line the way you would say it out loud: "Search was slow from a missing index", not "Search review: done" or "Slow search: missing index". Name any bug found and fixed on the way. Each line must stay true when read alone. Never mark something done that still waits on the user, and leave out anything the action items say. Under the summary, give at most three short lines that change what the user knows or must do. Then name in one line any work left that you can do yourself.

Then list the action items. Ask the call the user owns, such as merge, approve, or pick, and give your pick. A step you would take first goes in your pick. So does anything that must happen first, and anything that cannot be undone. Give the number or link of each PR, issue, or agent a call is about, also in a call between options.

Fit the shape to the call. A call about one item is one bullet: the call, your pick, what it changes for users, the evidence behind your pick, and its risk, with the item named once. When items share a call, write the call and your pick once, then give each item its own bullet, riskiest first: its link and name, what it changes for users, the evidence behind your pick, and its risk. Name an item's pick only where it differs from the call's. Give each item's risk even when it is low, such as "Low risk: only the colors change." Say what waiting costs only when it is more than a delay, such as a deadline or lost data.

For a call between options, give every option the work weighed, each with what it gets the user and what it costs, and the current state when there is one. Those costs are the call's risk, so add no separate risk line. When the screenshots above show the options, write each option's gain and cost under its screenshot.

## Controls

Assume the user remembers their last message and nothing after it.

Use [`/bro`](../bro/SKILL.md)'s voice, not its task: plain words, short sentences, no jargon, like one person catching up another. Say what changed for the user, not how you did it. Say "the tests pass", not "CI is green". Leave out hashes, file paths, commands, build numbers, and test counts unless the user needs one to act. Call each PR, branch, or agent by a name the user would know, not by a label you invented. If a fact needs context to make sense, give the context or leave the fact out.

An action item is a call or step only the user can take, such as a product choice, an approval, an irreversible action, or access you lack. Include any still waiting on the user, even one raised before their last message. Work you can still do yourself is not an action item. Never make up a call to fill the reply. A step the user did not ask for and the work does not need is not an action item, unless it is irreversible and waiting on the user: give it one line and no visual.

### Visuals

A visual is a picture: a screenshot, a video, a Mermaid diagram, a chart or diagram from `/visualize`, or a generated image. A Markdown table is not a visual, even with before and after columns.

When something is easier to grasp as a picture than as sentences, draw it: how a design or system works, a PR stack or dependency chain with each PR's state, a before and after of a fix, or options side by side. Never draw a status list, a list of action items, or boxes with nothing connecting them. Never give a fact twice, in text or across visuals.

Keep each visual small enough to read at a glance: at most six boxes, with at most eight words in each. Write labels as plain words a person would say, not tags like "Tests: pass". A fact that needs a sentence belongs in the text, or nowhere.

Embed screenshots and videos inline when the change is visible, not only as links. If a visible change has none, mark its summary line "No screenshot yet," and say there what changed on screen. Draw diagrams and charts from facts you have: a Mermaid diagram for how things connect and a `/visualize` chart for numbers. Never invent a number, and never draw or generate a picture of a screen you did not capture. Link only artifacts that exist.

## Constraints

Keep this turn read-only. Make visuals only from what you already have: do not change code, start an app or a job, or post anything.
