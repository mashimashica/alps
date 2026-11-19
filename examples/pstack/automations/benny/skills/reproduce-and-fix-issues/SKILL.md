---
name: reproduce-and-fix-issues
description: Reproduce triaged Slack bugs through a configured app-control adapter, verify existing fixes, and open a bounded draft pull request only after before-and-after proof. Use only from the configured Benny repro automation.
disable-model-invocation: true
---

# Reproduce and fix issues

## Purpose

Carry a triaged Slack bug toward a proven fix, no further than evidence from the target app's real UI supports: a repro of the exact symptom once a trusted triage marker is in the source thread, verification of an existing fix when one exists, and a bounded fix only after a confirmed repro.

## Outcomes

- Where a verdict meets the triage contract with a `bug` or `performance` marker and no person owns the fix, the operations thread or the run output carries the run's result: a confirmed repro, `Could not reproduce`, `Blocked`, or the outcome of verifying an existing fix.
- A repro reported as confirmed shows the exact discriminating symptom twice through real UI interaction, in two independent attempts, and a read-only media review confirms that the evidence visibly shows the discriminating broken state.
- An existing fix reported as verified shows the symptom on the baseline and its absence on the patched build, each through the real UI twice.
- Any pull request from the run is a draft backed by before-and-after proof: the baseline evidence, and on the patched build the broken state gone and the expected state in its place through the same real UI path, with no regression remaining.
- Every source-channel message from the run is a reply under `SOURCE_THREAD_TS`.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### 1. Freeze source coordinates

1. Require the trigger channel to equal the configured source channel.
2. Set `SOURCE_THREAD_TS` to `trigger.thread_ts` when present. Otherwise use `trigger.ts`.
3. Require a nonempty `SOURCE_THREAD_TS`.
4. Store `SOURCE_CHANNEL_ID` and `SOURCE_THREAD_TS` as immutable values.
5. Read the source thread and verify its root has those exact coordinates.
6. Fetch the source permalink.

### 2. Wait for the triage contract

1. Watch the source thread for the configured verdict budget. Stay silent while waiting.

2. Accept a verdict only when:

    - Its author matches `slack.triage_identity_user_id`.
    - It is a reply under `SOURCE_THREAD_TS`.
    - It contains exactly one configured marker.

    Public marker forms:

    ```text
    [benny:bug]
    [benny:bug] tracker=https://tracker.example/issue/123
    [benny:performance]
    [benny:performance] tracker=https://tracker.example/issue/123
    [benny:other]
    ```

3. Proceed only for `bug` or `performance`. Capture the optional tracker URL. Stop silently for `other`, a missing verdict, an untrusted author, conflicting markers, or a timeout.

    > NOTE This marker replaces private bot identities and free-form verdict matching.

### 3. Apply ownership and fix-artifact gates

1. Re-read the thread immediately before starting work.

#### Someone is explicitly fixing it

2. Stop when a person clearly claims the fix, gives a concrete implementation plan, or asks another agent to implement, patch, fix, or open a pull request.

    Do not treat these as fix ownership:

    - A bot summarizes evidence.
    - A tool looks up logs or tickets.
    - Someone asks a bot to diagnose, explain, inspect, or reproduce.
    - A bot posts a cause hypothesis without agreeing to implement it.

    Judge the requested action, not the presence of a bot.

#### A fix artifact already exists

3. If an open pull request or merged commit plausibly fixes this report, switch to `references/verify-existing-fix.md`. An artifact may come from the thread, tracker issue, repository history, or pull request search. A claim without a commit or pull request is not a fix artifact.

4. If a person owns the work but has not produced an artifact, stop. Do not race them.

### 4. Open an optional operations thread

1. If `slack.operations_channel_id` is configured, the coordinator may create one root status message there. This is the only allowed root post in the repro workflow.

2. Store its coordinates as `OPERATIONS_CHANNEL_ID` and `OPERATIONS_THREAD_TS`. Never confuse them with the source coordinates.

3. Use the configured plain Unicode status strings. Keep status text short:

    - Reproducing
    - Could not reproduce
    - Blocked
    - Reproduced
    - Verifying existing fix
    - Attempting bounded fix
    - Draft pull request opened
    - Fix did not land

4. Prefer configured Cursor Slack actions. Use `BENNY_SLACK_BOT_TOKEN` only when the user configured it for a narrow missing capability such as editing this one status message. Never expose the token to a worker.

5. If no operations channel is configured, keep detailed status in the automation run output. Do not substitute a source-channel root message.

### 5. Load and check the control adapter

1. Read `references/control-adapter.md` and the completed map at `control.feature_map_path`, then invoke the skill named by `control.skill_name`.

2. Find the feature-map section that matches the reported user path. Read it before driving the app. If no section covers the feature, mark the run blocked instead of inventing a path or selector.

3. Require all seven capabilities:

    1. Bring up the configured target app and test environment.
    2. Navigate the mapped feature and exercise its documented states.
    3. Drive the real UI with clicks, typing, keys, scrolling, drag, resize, or navigation.
    4. Inspect state without mutating it.
    5. Capture screenshots.
    6. Start and stop a screen recording.
    7. Clean up processes, sessions, profiles, and temporary data.

4. If the adapter is absent or any required capability is missing, mark the operations status as blocked and stop. Do not pretend a screenshot, unit test, state mutation, or source reading is a UI repro.

### 6. Study the report

1. Read the full source thread and tracker issue when present.

2. Collect:

    - Exact action path
    - Expected behavior
    - Observed behavior
    - Discriminating state where they diverge
    - Frequency
    - Version, environment, and platform
    - Attachments and error signatures
    - Candidate code area

3. Inspect screenshots and video.

4. Use read-only parallel workers for code history, test ideas, blast-radius mapping, and media review when useful. Each worker gets a narrow question and the Slack-write prohibition.

5. Trace the action through the repository. Use pstack's `why` skill for regression history and defensive code.

6. Form competing cause hypotheses and identify evidence that would separate them.

### 7. Reproduce

1. Bring up the target app through the control adapter.

2. Confirm the correct app, workspace, account, data set, and feature state before acting. Use stable app markers. Do not rely on window order or a familiar title alone.

3. Drive the reported path through real UI actions.

4. Before calling it reproduced:

    1. Name the correct final state.
    2. Name the broken final state.
    3. Reach the point where they diverge.
    4. Observe the broken state.
    5. Reset enough state to make the second attempt independent.
    6. Repeat the same path and observe the same broken state again.
    7. Cross-check a real state value when possible.

    An expected dialog, loading state, or setup step is not the bug. Capture the final state that distinguishes correct from broken behavior.

5. Use the configured repro budget. If the symptom does not reproduce within it, report a clean `Could not reproduce` outcome. If the environment cannot provide a required capability, report `Blocked` and state what was missing.

### 8. Capture and review evidence

1. For a successful repro:

    - Record the full path through the symptom.
    - Capture a screenshot of the broken final state.
    - Save a short note with the exact steps and observed state.
    - Keep artifacts in the configured temporary artifact directory.

2. Have a read-only media reviewer answer one question: does the evidence visibly show the discriminating broken state? If the answer is no or uncertain, the repro is not confirmed. Capture better evidence or use `Could not reproduce`.

3. Post detailed evidence only in the operations thread when configured. Keep the source update concise.

### 9. Report the repro outcome

1. Update the operations status first.

2. For `Could not reproduce` or `Blocked`, post nothing in the source thread. The operations thread or run output carries the result.

3. For a confirmed repro, run the source preflight and post at most one unprompted source reply:

    - Say the issue reproduced.
    - Link the operations evidence thread when one exists.
    - Include at most three short findings.
    - Link the tracker issue when one exists.
    - Do not ping an owner by default.

    Attach evidence only when the configured Slack action keeps it inside the same source thread and the organization's retention policy allows it.

4. Wait for the configured rejection window. If a person shows that the setup or interpretation was wrong, correct the repro once. Do not start the fix phase until the window closes without a valid rejection.

### 10. Verify an existing fix

1. When a fix artifact exists, follow `references/verify-existing-fix.md`. Verification must show the symptom on the baseline and its absence on the patched build. Both paths use the real UI twice. Do not edit the existing fix, add a competing patch, or open a replacement pull request.

### 11. Qualify a bounded fix

1. Attempt a fix only when all of these hold:

    - The outcome is a plain confirmed repro.
    - Media review confirmed the broken final state.
    - No existing fix artifact appeared.
    - No person claimed the fix during the rejection window.
    - Runtime evidence identifies the root cause.
    - The likely change fits the configured fix budget and repository scope.
    - The control adapter can run both baseline and patched builds.

    If any condition fails, keep the repro report and stop without a pull request.

2. When the gate passes, update operations status to `Attempting bounded fix`.

### 12. Root-cause and implement

1. Read-only workers may:

    - Trace code and history
    - Propose tests
    - Map blast radius
    - Review a diff
    - Review media

    They do not edit, run external writes, post status, or own the fix.

2. A tightly scoped code edit may be delegated during this phase only when tool isolation removes Slack credentials and every Slack write action from that worker. Its prompt must still carry the explicit Slack-write ban. The coordinator reviews the edit and runs or verifies the required tests. If tool isolation is uncertain, keep the edit in the coordinator.

3. Confirm the mechanism with runtime evidence. Eliminate competing hypotheses before editing.

4. Fix the root cause with the smallest justified change.

    - Invoke pstack's `tdd` skill when there is a cheap local test target, and write the failing test before the fix.
    - State why TDD was skipped when the path is expensive, unclear, or integration-heavy.
    - Keep unrelated cleanup out.
    - Stop if the change grows beyond the configured effort or risk budget.

### 13. Prove the fix

1. Keep the original baseline evidence.

2. On the patched build:

    1. Run the same real UI path.
    2. Repeat it twice.
    3. Show that the broken state is gone.
    4. Show the expected state in its place.
    5. Capture an after recording and screenshot.
    6. Cross-check the same real state value used for the baseline.

    A compile, unit test, code review, or plausible diff is not after evidence.

3. Run focused tests, then smoke the blast radius around the changed behavior. Cover nearby states, inputs, permissions, platforms, and failure paths that the change could affect. Stop without a pull request if a regression remains.

### 14. Open a draft pull request

1. Only after before-and-after proof:

    - Review the final diff for unrelated changes and secrets.
    - Run the repository's required checks.
    - Create small ordered commits when the repository workflow allows it.
    - Open a draft pull request.
    - Link the configured tracker issue using the tracker's supported pull request syntax.
    - Use the configured public URL form, normally `https://github.com/{owner}/{repo}/pull/{number}`.
    - Include the repro steps, root cause, test result, before and after evidence, and blast-radius checks.
    - Run the pull request text and all Slack updates through pstack's `unslop` skill.

2. If pull request creation fails, do not claim success. Keep the commit or branch state in the run output and mark operations status `Fix did not land`.

3. On success, mark operations status `Draft pull request opened` and post one concise reply in the operations thread with the linked pull request. Do not create a second source-channel root or unprompted source reply.

### 15. Follow-ups and cleanup

1. Watch the configured operations thread for one follow-up window.

    - Answer a direct question from evidence already gathered.
    - Apply one concrete correction and rerun the repro once when it invalidates the setup.
    - Stay out of human coordination and side chatter.
    - Stop when asked.

2. Always call the control adapter's cleanup capability. Keep artifacts only as long as the configured retention policy allows.

## Controls

- Use pstack's `principle-guard-the-context-window` for delegated analysis.
- Apply pstack's `principle-sequence-verifiable-units`, `principle-fix-root-causes`, and `principle-prove-it-works` through repro, fix, and verification.

## Constraints

Use only from the configured Benny repro automation.

Unless a Task states otherwise, work the Activities and their Tasks in the order listed. These dependencies are required.

- Step 1 comes before making a work list or delegating.
- Nothing after step 2 starts unless step 2 accepts a `bug` or `performance` verdict.
- The control adapter is loaded and checked in step 5 before the app is driven in step 7.
- The media review of step 8 confirms a repro before step 9 reports it.
- The fix phase does not start until the rejection window of step 9 closes without a valid rejection.
- The gate of step 11 passes before any edit in step 12.
- The baseline evidence of steps 7 and 8 exists before the fix, and step 13 keeps it and checks the patched build against it.
- Step 14 comes only after the before-and-after proof of step 13.

Never replace the stored `SOURCE_CHANNEL_ID` and `SOURCE_THREAD_TS` with a reply timestamp, operations timestamp, or status-message timestamp.

Before every source-channel post:

1. Read the thread by the immutable coordinates.
2. Confirm the parent exists, is not deleted, and still belongs to the source channel.
3. Send only with `channel=SOURCE_CHANNEL_ID` and `thread_ts=SOURCE_THREAD_TS`.
4. Read the thread again and verify the new message is a reply.

If any check fails, post nothing. Never retry at the root or in a fallback channel.

The coordinator owns every Slack post, the final diff review, commits, and the pull request.

Never merge or deploy from this workflow.

### Hard safety rules

- Freeze the source channel and root thread coordinates before doing any work.
- Never post a root message in the source channel.
- Preflight the source parent before every source-thread post.
- The coordinator is the only Slack poster.
- Delegated analysis workers are read-only and return findings or media notes.
- A fix-phase code worker may edit only when its environment provably excludes Slack credentials and every Slack write action. Otherwise the coordinator edits.
- Every child prompt must explicitly forbid `SendSlackMessage`, `PostToSlack`, `chat.postMessage`, and all other Slack writes.
- Never give a child a Slack token, posting instructions, source coordinates for posting, or permission to report externally.
- If a child needs Slack write access to run, do not launch it.
- Utility bots are evidence sources. They do not own the fix unless a person explicitly delegated the fix to them.
- The exact discriminating symptom must appear twice through real UI interaction.
- State inspection may confirm an observation. It must not inject or force the symptom.
- No confirmed repro means no authored fix.
- Existing pull requests or commits switch the run to verify mode. Do not author over them.
- Use `github.com` pull request links.
- Keep captures, recordings, logs, and tokens out of source control.

## Entry Criteria

Load the external Benny configuration supplied by the automation. If the config, required actions, control adapter, or completed feature map is missing, fail closed.
