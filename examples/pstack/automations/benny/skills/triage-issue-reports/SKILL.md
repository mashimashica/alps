---
name: triage-issue-reports
description: Triage Slack issue reports with one thread-only verdict, evidence review, cause-aware routing, tracker dedupe, and fail-closed ticket creation. Use only from the configured Benny triage automation.
disable-model-invocation: true
---

# Triage issue reports

## Purpose

Give one Slack report a classification and one useful verdict in its source thread, and a tracker issue only when it is a clear, new bug. Reproducing or fixing the bug is outside this skill.

## Outcomes

- The source thread holds exactly one verdict from the run, a reply under `SOURCE_THREAD_TS` that ends with exactly one configured marker line, unless a condition this skill states ended the run before the verdict.
- Every Slack message from the run is a reply under the source thread's root. None is a root message, a broadcast reply, a DM, or a post in another channel or a replacement thread.
- The verdict leads with the outcome that the thread's evidence and, where cause tracing was available, the cause trace support.
- What could not be established (an unreadable attachment, unavailable cause tracing, an unclear owner, an uncertain tracker match) is stated as such, not invented or guessed.
- A tracker issue from the run exists only for a bug or performance report whose behavior is clearly broken, that is still live or not known to be fixed, and that has no confident or plausible live match in the tracker.
- A created issue is self-contained and links back to the source thread.
- Where dedupe found a confident duplicate and no stop or fail-closed condition applied, the existing issue carries the source permalink and one short recurrence note.
- Where the run created a tracker issue and its verdict did not land, the issue is verified canceled, closed, or deleted, or the failure is reported only in the automation run output.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### 1. Freeze source coordinates

1. Read `source_channel_id` from the trigger.
2. Require it to equal the configured source channel.
3. Set `SOURCE_THREAD_TS` to `trigger.thread_ts` when present. Otherwise use `trigger.ts`.
4. Require a nonempty `SOURCE_THREAD_TS`.
5. Store `SOURCE_CHANNEL_ID` and `SOURCE_THREAD_TS` as immutable values.
6. Read the thread and verify that its root has exactly those coordinates.
7. Fetch a stable source permalink.

### 2. Read the whole report

1. Read the root and current replies before deciding.

2. Capture:

    - Reporter wording
    - Product version, app build, environment, and platform when present
    - Expected behavior
    - Observed behavior
    - Frequency and trigger
    - Error text or stack signature
    - Existing issue, commit, or pull request links
    - Any explicit statement that someone is already fixing it

3. Inspect every relevant attachment.

    - Read screenshots at full useful resolution.
    - Review video for the state transition that separates correct and broken behavior.
    - Read logs, traces, and crash text for concrete signatures.
    - If media needs specialist review, use a read-only media worker and ask a narrow question. The worker returns findings only.
    - If an attachment cannot be read, say so in the verdict. Do not invent what it shows.

4. Use evidence already in the thread before asking the reporter for more.

### 3. Trace cause before routing

1. Do a bounded source and history pass before choosing an owner or destination. Trace the path from the reported action to the observed result. Use pstack's `why` skill when the report looks like a regression or touches defensive code.

    1. Identify the likely code path from the reported action to the observed result.
    2. Check whether the visible symptom belongs to that code path or a dependency below it.
    3. Check recent changes when the report looks like a regression.
    4. Check whether a merged commit or open pull request already addresses the same symptom.
    5. Separate confirmed facts from hypotheses.

    This pass does not need a complete root cause. It must be strong enough to avoid routing a visible symptom to the wrong owner.

2. If the repository cannot be read, do not guess a code owner. Continue with a conservative classification and say that cause tracing was unavailable.

### 4. Classify

1. Choose one category.
2. When the bug versus feature line is unclear, do not file. The one verdict may ask one focused question and use the `other` marker.

#### Bug

Something violates intended behavior. Examples include wrong output, broken state, an error, a crash, a hang, a silent no-op, or a regression.

#### Performance

The report describes measurable slowness, excess memory, battery drain, jank, or another resource problem. Treat it as a bug, but preserve measurements and profiles.

#### Feature request

The current behavior appears intentional and the reporter wants a different behavior or affordance.

#### Question or feedback

The report asks how something works, expresses a preference without a concrete defect, or gives general feedback.

#### Reroute

Cause tracing shows that another configured destination owns the issue.

### 5. Apply configured routing

1. Read the optional routing map from `routing.map_path`.

    - Match on confirmed product area, code path, or error signature.
    - A visible symptom alone is not enough when cause tracing points elsewhere.
    - If no route matches, say the owner is unclear. Do not guess.
    - Do not cross-post. Tell the reporter where to take the issue in the source thread.

### 6. Use the issue-tracker adapter

1. Resolve configured team, project, status, and labels at runtime. Do not invent IDs, create labels, assign owners, or set priority unless the config explicitly requires it.

### 7. Dedupe

1. Always check whether this source permalink is already linked to a tracker issue or a prior triage reply. If so, do not post or create a duplicate.

2. For bugs and performance reports, search the tracker using:

    - Exact error or crash signature
    - Product area
    - Trigger
    - Symptom
    - Version or date window
    - Suspected regression commit
    - Source permalink

3. Choose one outcome:

    - Confident duplicate: same signature, or the same area, trigger, and symptom, or a confirmed shared cause.
    - Possibly related: a shared cause is plausible but not proven.
    - Weak resemblance: similarity is superficial.
    - No match.

    A long-closed issue is a regression lead, not automatically a live duplicate.

4. For a confident duplicate, update the existing issue with the source permalink and one short recurrence note. Do not reopen, relabel, or reassign it unless the config says to.

5. For a possible match, link it in the verdict as uncertain and create nothing.

### 8. Decide whether to create

1. Create only when all of these are true:

    1. The classification is bug or performance.
    2. The behavior is clearly broken.
    3. The issue is still live or not known to be fixed.
    4. Dedupe found no confident or plausible live match.
    5. The source parent and permalink passed preflight.
    6. The tracker target fields resolved.
    7. The adapter can compensate if the verdict post fails.

    Never create for a feature request, question, feedback item, reroute, possible duplicate, confident duplicate, or already-fixed issue.

    The new issue must be self-contained:

    - Plain title that names the area and symptom
    - Reporter quote
    - Expected and observed behavior
    - Version and environment, or `unknown`
    - Trigger and frequency
    - Source thread permalink
    - Short cause-tracing findings with hypotheses labeled as hypotheses
    - Inline screenshot or representative video frame when supported
    - Links to remaining artifacts
    - Configured intake status and labels

    Do not put a guessed root cause in the title.

### 9. Post one verdict

1. Run a fresh source-parent preflight.

2. Then post exactly one reply with `channel=SOURCE_CHANNEL_ID` and `thread_ts=SOURCE_THREAD_TS`. Keep the reply short:

    - Lead with the outcome.
    - Link the existing or new tracker issue when there is one.
    - Mention a reroute or one missing fact when needed.
    - Include at most one allowed owner ping.
    - End with exactly one marker line.

    Marker contract:

    ```text
    [benny:bug]
    [benny:bug] tracker=https://tracker.example/issue/123
    [benny:performance]
    [benny:performance] tracker=https://tracker.example/issue/123
    [benny:other]
    ```

    Use only the configured marker strings. The repro automation trusts the marker only when it comes from the configured triage identity in this source thread.

3. After posting, read the same source thread and verify the verdict appears under `SOURCE_THREAD_TS`. If it does not, never retry at the root.

4. If this run created a tracker issue and the verdict did not land, use the adapter's compensation action. Verify that the issue is canceled, closed, or deleted. If compensation cannot be verified, report the failure only in the automation run output.

### 10. Watch one follow-up window

1. Watch the source thread for the configured follow-up window, then stop.

    - Answer only a direct question to the triage identity.
    - Apply a concrete correction to the tracker issue when safe.
    - Do not emit a second marker in the same run.
    - Stay out of human coordination and side chatter.
    - Stop early if someone asks the automation to stop.

    Do not extend the window more than once. A new report should start a new run.

## Controls

- Apply pstack's `principle-separate-before-serializing-shared-state` to source coordinates.
- Apply pstack's `principle-minimize-reader-load` and `unslop` skills to the final verdict.

## Constraints

Use only from the configured Benny triage automation. Create a tracker issue only for a clear, new bug. Do not reproduce or fix it here.

Unless a Task states otherwise, work the Activities in the order listed. Within an Activity, Tasks may be worked in any order unless one states otherwise. These dependencies are required.

- Step 1 comes before making a work list or delegating.
- The Tasks of step 1, and the numbered actions under a Task, are worked in the order listed.
- The root and current replies are read in step 2 before deciding.
- Cause tracing in step 3 comes before choosing an owner or destination in step 5.
- In step 7 one outcome is chosen from the tracker search, and the update for a confident duplicate or the link for a possible match follows that choice.
- Step 8 decides whether to create only after step 6 has resolved the tracker target fields and step 7 has deduped.
- In step 9 the fresh source-parent preflight comes before the verdict post, the read that verifies the verdict comes after it, and compensation follows that read.

Every source read and post after step 1 must use the stored `SOURCE_CHANNEL_ID` and `SOURCE_THREAD_TS`. Never replace them with a reply timestamp or an operations-thread timestamp.

Never call a source-channel posting action without a nonempty `thread_ts`.

If a required operation of the configured adapter is unavailable, fail closed for that write.

Owner pings are off by default. A ping is allowed only when all of these hold:

1. The routing map explicitly names the owner.
2. The config allows that ping type.
3. The item is a feature request that needs owner input, or recent history identifies a likely regression author with strong evidence.
4. The owner is not a broad on-call group.

No other case gets a ping.

### Hard safety rules

- The source channel and root thread coordinates are immutable.
- Never post a root message in the source channel.
- Never post to another channel, broadcast a reply, send a DM, or start a replacement thread.
- Preflight the source parent before any tracker write and immediately before the verdict post.
- If the parent is missing, deleted, inaccessible, or uncertain, stop with no writes.
- Post one substantive verdict. Do not narrate progress.
- The coordinator is the only Slack poster.
- Delegated workers return findings only. They must be read-only and receive no Slack credentials or write actions.
- Every child prompt must forbid `SendSlackMessage`, `PostToSlack`, `chat.postMessage`, and every other Slack write.
- If worker isolation cannot enforce those limits, do the work in the coordinator.
- Never create an issue that cannot link back to the source thread.
- Prefer no ticket over a guessed or duplicate ticket.

## Entry Criteria

Load the external Benny configuration supplied by the automation. If the config is missing, malformed, or incomplete, stop without posting or writing to the tracker.

## Enablers

The tracker is an adapter, not a required vendor. A Linear adapter is one valid example. A GitHub Issues adapter or another tracker may implement the same contract.

The configured adapter must provide:

- Search issues by text, state, label, source URL, and date range
- Read one issue and its links
- Create an issue with title, body, status, labels, and source URL
- Update an existing issue without replacing unrelated fields
- Add a source link and recurrence note
- Cancel, close, or delete an issue created by this run if the Slack handoff fails
