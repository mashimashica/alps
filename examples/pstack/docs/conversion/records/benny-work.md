# Conversion record: Benny: triage, reproduce and fix

[Conversion guide](../README.md)

## `automations/benny/skills/triage-issue-reports/SKILL.md`

Title: Triage issue reports. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Give one Slack report a classification and one useful verdict in its source thread, and a tracker issue only when it is a clear, new bug. Reproducing or fixing the bug is outside this skill.

| Outcome | Basis in the upstream text |
| --- | --- |
| The source thread holds exactly one verdict from the run, a reply under `SOURCE_THREAD_TS` that ends with exactly one configured marker line, unless a condition this skill states ended the run before the verdict. | Hard safety rules: "Post one substantive verdict." Step 9: "Then post exactly one reply with `channel=SOURCE_CHANNEL_ID` and `thread_ts=SOURCE_THREAD_TS`.", "End with exactly one marker line.", "Use only the configured marker strings.", "After posting, read the same source thread and verify the verdict appears under `SOURCE_THREAD_TS`." The exception covers the paths on which upstream ends the run without a verdict: "If the config is missing, malformed, or incomplete, stop without posting or writing to the tracker.", "If the parent is missing, deleted, inaccessible, or uncertain, stop with no writes.", and step 7 "If so, do not post or create a duplicate." |
| Every Slack message from the run is a reply under the source thread's root. None is a root message, a broadcast reply, a DM, or a post in another channel or a replacement thread. | Hard safety rules: "Never post a root message in the source channel.", "Never post to another channel, broadcast a reply, send a DM, or start a replacement thread.", "The coordinator is the only Slack poster." Step 9: "Never call a source-channel posting action without a nonempty `thread_ts`.", "If it does not, never retry at the root." setup-benny step 8 tests the same result ("No source-channel root message appears."). |
| The verdict leads with the outcome that the thread's evidence and, where cause tracing was available, the cause trace support. | Step 9: "Lead with the outcome." Step 2: "Read the root and current replies before deciding." Step 3: "Separate confirmed facts from hypotheses." The condition "where cause tracing was available" covers upstream's permitted path "If the repository cannot be read, do not guess a code owner. Continue with a conservative classification and say that cause tracing was unavailable." (amendment 15.3). |
| What could not be established (an unreadable attachment, unavailable cause tracing, an unclear owner, an uncertain tracker match) is stated as such, not invented or guessed. | Step 2: "If an attachment cannot be read, say so in the verdict. Do not invent what it shows." Step 3: "If the repository cannot be read, do not guess a code owner. ... say that cause tracing was unavailable." Step 5: "If no route matches, say the owner is unclear. Do not guess." Step 7: "For a possible match, link it in the verdict as uncertain and create nothing." Split from the former third Outcome because it is assessable independently of the lead outcome. |
| A tracker issue from the run exists only for a bug or performance report whose behavior is clearly broken, that is still live or not known to be fixed, and that has no confident or plausible live match in the tracker. | Lead paragraph: "Create a tracker issue only for a clear, new bug." Step 8, conditions 1 to 4 of "Create only when all of these are true" and "Never create for a feature request, question, feedback item, reroute, possible duplicate, confident duplicate, or already-fixed issue." Hard safety rules: "Prefer no ticket over a guessed or duplicate ticket." Conditions 5 to 7 of step 8 are gates on the action and stay in the step. |
| A created issue is self-contained and links back to the source thread. | Step 8: "The new issue must be self-contained:" with its list, which includes "Source thread permalink". Hard safety rules: "Never create an issue that cannot link back to the source thread." |
| Where dedupe found a confident duplicate and no stop or fail-closed condition applied, the existing issue carries the source permalink and one short recurrence note. | Step 7: "For a confident duplicate, update the existing issue with the source permalink and one short recurrence note." The exception covers the paths on which upstream forbids the write: "Preflight the source parent before any tracker write", "If the parent is missing, deleted, inaccessible, or uncertain, stop with no writes.", and step 6 "If a required operation is unavailable, fail closed for that write." |
| Where the run created a tracker issue and its verdict did not land, the issue is verified canceled, closed, or deleted, or the failure is reported only in the automation run output. | Step 9: "If this run created a tracker issue and the verdict did not land, use the adapter's compensation action. Verify that the issue is canceled, closed, or deleted. If compensation cannot be verified, report the failure only in the automation run output." |

Carried from the frontmatter description into the body:

- Use only from the configured Benny triage automation.

Order dependencies stated under Constraints, with the reason for each:

- Default: the Activities (upstream steps 1 to 10, numbered upstream) are worked in the order listed. Within an Activity, Tasks formed from unnumbered paragraphs set no order (amendment 15.2).
- Step 1 comes before making a work list or delegating. Reason: upstream order word, "Before making a work list or delegating:".
- The Tasks of step 1, and the numbered actions under a Task (step 3, Task 1, items 1 to 5), are worked in the order listed. Reason: upstream numbered them, and later items use earlier results ("verify that its root has exactly those coordinates", "that code path"). Step 8's numbered conditions and the owner-ping conditions are conditions, not actions.
- The root and current replies are read in step 2 before deciding. Reason: upstream order word, "Read the root and current replies before deciding."
- Cause tracing in step 3 comes before choosing an owner or destination in step 5. Reason: upstream heading "Trace cause before routing" and "Do a bounded source and history pass before choosing an owner or destination."
- In step 7 one outcome is chosen from the tracker search, and the update for a confident duplicate or the link for a possible match follows that choice. Reason: the later Tasks use a result only the earlier one produces ("Choose one outcome:", "For a confident duplicate", "For a possible match").
- Step 8 decides whether to create only after step 6 has resolved the tracker target fields and step 7 has deduped. Reason: step 8 conditions 4 and 6 use results only those steps produce.
- In step 9 the fresh source-parent preflight comes before the verdict post, the read that verifies the verdict comes after it, and compensation follows that read. Reason: upstream order words, "Run a fresh source-parent preflight. Then post ..." and "After posting, read the same source thread ..."; compensation applies when "the verdict did not land", which only the read establishes.
- Stated in the Hard safety rules list, also under Constraints: "Preflight the source parent before any tracker write and immediately before the verdict post."
- Stated in Constraints: "Every source read and post after step 1 must use the stored `SOURCE_CHANNEL_ID` and `SOURCE_THREAD_TS`."

State-changing or external effects the work can have, with the condition upstream states:

- Post the verdict as a Slack reply in the source thread. Conditions: configuration loaded and complete; a fresh source-parent preflight immediately before the post; exactly one reply with `channel=SOURCE_CHANNEL_ID` and a nonempty `thread_ts=SOURCE_THREAD_TS`; only the coordinator posts; never a root message, another channel, a broadcast, a DM, or a replacement thread; no post when the source permalink is already linked to a tracker issue or a prior triage reply; never retried at the root.
- Post follow-up replies in the source thread during the one follow-up window. Conditions: only to answer a direct question to the triage identity; no second marker in the same run; the window is not extended more than once; stop early if someone asks.
- Mention (ping) an owner in the verdict. Conditions: off by default; at most one; allowed only when the routing map explicitly names the owner, the config allows that ping type, the item is a feature request that needs owner input or recent history identifies a likely regression author with strong evidence, and the owner is not a broad on-call group.
- Create a tracker issue. Conditions: all seven conditions of step 8; never for a feature request, question, feedback item, reroute, possible duplicate, confident duplicate, or already-fixed issue; the issue must link back to the source thread; IDs, labels, owners, and priority are not invented or set unless the config explicitly requires it; preflight before the write; fail closed when a required adapter operation is unavailable.
- Update an existing tracker issue for a confident duplicate with the source permalink and one short recurrence note. Conditions: preflight before the write; do not reopen, relabel, or reassign unless the config says to.
- Cancel, close, or delete a tracker issue this run created (compensation). Condition: only when the verdict did not land; the result is verified; an unverified compensation is reported only in the automation run output.
- Apply a concrete correction to the tracker issue during the follow-up window. Condition: when safe.

Also: 14 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `automations/benny/skills/reproduce-and-fix-issues/SKILL.md`

Title: Reproduce and fix issues. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Carry a triaged Slack bug toward a proven fix, no further than evidence from the target app's real UI supports.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where a verdict meets the triage contract with a `bug` or `performance` marker and no person owns the fix, the operations thread or the run output carries the run's result as its evidence supports it. The result is a confirmed repro, `Could not reproduce` when the symptom did not reproduce within the configured repro budget or the media review did not confirm it, `Blocked`, which states what was missing when the environment cannot provide a required capability, or the outcome of verifying an existing fix. | Step 2: "Proceed only for `bug` or `performance`." Step 3: the two stop rules for a person who owns the fix. Step 7: "Use the configured repro budget. If the symptom does not reproduce within it, report a clean `Could not reproduce` outcome. If the environment cannot provide a required capability, report `Blocked` and state what was missing." Step 8: "If the answer is no or uncertain, the repro is not confirmed. Capture better evidence or use `Could not reproduce`." Step 5: "mark the run blocked", "mark the operations status as blocked and stop" (no statement of what was missing is required there, so the Outcome ties that requirement to step 7's condition). Step 9: "Update the operations status first.", "The operations thread or run output carries the result." Step 4: "If no operations channel is configured, keep detailed status in the automation run output." Step 10 and verify-existing-fix.md: "Keep the result in the operations thread or run output." |
| A repro reported as confirmed shows the exact discriminating symptom twice through real UI interaction, in two independent attempts, and a read-only media review confirms that the evidence visibly shows the discriminating broken state. | Hard safety rules: "The exact discriminating symptom must appear twice through real UI interaction." Step 7, items 4 to 6: "Observe the broken state.", "Reset enough state to make the second attempt independent.", "Repeat the same path and observe the same broken state again." Step 8: "Have a read-only media reviewer answer one question: does the evidence visibly show the discriminating broken state?", "If the answer is no or uncertain, the repro is not confirmed." |
| An existing fix reported as verified shows the symptom on the baseline and its absence on the patched build, each through the real UI twice. | Step 10: "Verification must show the symptom on the baseline and its absence on the patched build. Both paths use the real UI twice." |
| Any pull request from the run is a draft. | Step 14: "Open a draft pull request." Description: "open a bounded draft pull request only after before-and-after proof". Split from the former fourth Outcome because draft state and proof are assessable independently. |
| Any pull request from the run rests on before-and-after proof. The original baseline evidence is kept, and on the patched build the same real UI path, run and repeated twice, shows the broken state gone and the expected state in its place, with no regression remaining. | Step 14: "Only after before-and-after proof:". Step 13: "Keep the original baseline evidence.", items 1 to 4 of "On the patched build:" ("Run the same real UI path.", "Repeat it twice.", "Show that the broken state is gone.", "Show the expected state in its place."), "A compile, unit test, code review, or plausible diff is not after evidence.", "Stop without a pull request if a regression remains." Hard safety rules: "No confirmed repro means no authored fix." The words "run and repeated twice" keep upstream's count ambiguity. |
| Every source-channel message from the run is a reply under `SOURCE_THREAD_TS`. | Hard safety rules: "Never post a root message in the source channel.", "Preflight the source parent before every source-thread post." Step 1: "Send only with `channel=SOURCE_CHANNEL_ID` and `thread_ts=SOURCE_THREAD_TS`.", "Read the thread again and verify the new message is a reply.", "Never retry at the root or in a fallback channel." Step 4: "Do not substitute a source-channel root message." Step 14: "Do not create a second source-channel root or unprompted source reply." |

Carried from the frontmatter description into the body:

- Use only from the configured Benny repro automation.

Order dependencies stated under Constraints, with the reason for each:

- Default: the Activities (upstream steps 1 to 15, numbered upstream) are worked in the order listed, unless a Task states otherwise (step 3 switches to verify mode). Within an Activity, Tasks formed from unnumbered paragraphs set no order (amendment 15.2).
- Step 1 comes before making a work list or delegating. Reason: upstream order word, "Before making a work list or delegating:". The hard safety rule "Freeze the source channel and root thread coordinates before doing any work." states the same.
- The Tasks of step 1, and the numbered actions under a Task (step 7 Task 4 items 1 to 7, step 13 Task 2 items 1 to 6), are worked in the order listed. Reason: upstream numbered them, and later items use earlier results ("Repeat the same path", "the same real state value used for the baseline"). Step 5's seven capabilities are requirements, not actions.
- In step 2 a verdict is accepted before its marker decides whether the run proceeds. Reason: "Proceed only for `bug` or `performance`" uses the marker of the accepted verdict.
- Nothing after step 2 starts unless step 2 accepts a `bug` or `performance` verdict. Reason: gate, "Proceed only for `bug` or `performance`." and "Stop silently for ...".
- In step 4 the root status message exists before its coordinates are stored. Reason: "Store its coordinates" uses a result only the root status message produces.
- In step 5 the completed map is read before its matching section is found. Reason: "Find the feature-map section" uses the map that "Read ... the completed map at `control.feature_map_path`" supplies.
- The control adapter is loaded and checked in step 5 before the app is driven in step 7. Reason: "Read it before driving the app." and the gate "If the adapter is absent or any required capability is missing, mark the operations status as blocked and stop."
- In step 7 the app is brought up before it is confirmed and driven. Reason: confirming "the correct app" and driving the path use the app that "Bring up the target app" produces; "before acting" orders confirmation before driving.
- In step 8 the evidence is captured before the media review, and the media review confirms a repro before step 9 reports it. Reason: the review judges "the evidence"; gate, "If the answer is no or uncertain, the repro is not confirmed." Step 9 posts "For a confirmed repro".
- In step 9 the rejection window follows the repro report. Reason: a person rejects the reported repro ("If a person shows that the setup or interpretation was wrong, correct the repro once.").
- The fix phase does not start until the rejection window of step 9 closes without a valid rejection. Reason: upstream order word, "Do not start the fix phase until ...".
- The gate of step 11 passes before any edit in step 12. Reason: gate, "Attempt a fix only when all of these hold" and "When the gate passes".
- The baseline evidence of steps 7 and 8 exists before the fix, and step 13 keeps it and checks the patched build against it. Reason: baseline, "Keep the original baseline evidence." and "Cross-check the same real state value used for the baseline."
- Step 14 comes only after the before-and-after proof of step 13. Reason: upstream order words, "Only after before-and-after proof:".
- In step 14 the handling of a failed or successful pull request creation follows the attempt to open it. Reason: "If pull request creation fails" and "On success" use the result of opening the draft pull request.
- Stated in Constraints as a relocated rule: "Before every source-channel post:" with its four checks.
- Stated in the Hard safety rules list: "Preflight the source parent before every source-thread post."

State-changing or external effects the work can have, with the condition upstream states:

- Create one root status message in the operations channel and update its status. Conditions: only if `slack.operations_channel_id` is configured; the coordinator creates it; it is the only allowed root post in the repro workflow; never substituted by a source-channel root message.
- Post one reply in the source thread for a confirmed repro. Conditions: the source preflight (read by the immutable coordinates, confirm the parent, send only with `channel=SOURCE_CHANNEL_ID` and `thread_ts=SOURCE_THREAD_TS`, read back and verify it is a reply); at most one unprompted source reply; no owner ping by default; nothing is posted in the source thread for `Could not reproduce` or `Blocked`; if any check fails, post nothing and never retry at the root or in a fallback channel; only the coordinator posts.
- Attach evidence in the source thread. Condition: only when the configured Slack action keeps it inside the same source thread and the organization's retention policy allows it.
- Post detailed evidence and one reply with the linked pull request in the operations thread. Conditions: only when the operations thread is configured; the pull request reply only on success.
- Use `BENNY_SLACK_BOT_TOKEN`. Conditions: only when the user configured it for a narrow missing capability such as editing the one status message; never exposed to a worker.
- Bring up, drive, record, and clean up the target app through the control adapter. Conditions: all seven capabilities present; the feature-map section covers the reported path; real UI actions only; state inspection must not inject or force the symptom; cleanup is always called.
- Write captures, recordings, logs, and notes. Conditions: kept in the configured temporary artifact directory, out of source control, only as long as the configured retention policy allows.
- Edit code for a bounded fix, by the coordinator or a delegated worker. Conditions: all seven conditions of step 11 (a plain confirmed repro, media review, no existing fix artifact, no person claimed the fix during the rejection window, runtime evidence of the root cause, fit to the fix budget and repository scope, adapter can run both builds); the rejection window closed without a valid rejection; delegation only when tool isolation removes Slack credentials and every Slack write action; stop if the change grows beyond the configured effort or risk budget.
- Create commits and open a draft pull request, with a link to the configured tracker issue. Conditions: only after before-and-after proof; final diff reviewed for unrelated changes and secrets; required checks run; no regression remaining; the coordinator owns commits and the pull request; never merge or deploy from this workflow; on failure, do not claim success.
- Verify mode (references/verify-existing-fix.md): one source-thread reply for a Confirmed outcome after the source preflight. Conditions: do not edit the existing fix, add a competing patch, or open a replacement pull request.

Also: 14 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md`

Title: Verify an existing fix. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Establish whether an existing pull request or commit resolves the reported symptom, from the baseline and the patched build running under the same conditions. Authoring or changing a fix is outside this mode.

| Outcome | Basis in the upstream text |
| --- | --- |
| The run reports one verification outcome, Confirmed, Insufficient fix, or Inconclusive, and it matches what the baseline and the patched build showed. | The upstream section "Outcomes" with its three subsections and their defining sentences: "The baseline reproduces twice and the patched build resolves it twice.", "The symptom appears on both baseline and patched builds.", "The baseline does not reproduce, the patched app cannot run, or the evidence does not show the discriminating state." Reporting: "Mark operations status as verified.", "Mark operations status as reproduced but not fixed.", "Keep the result in the operations thread or run output." |
| A Confirmed outcome rests on the symptom reproducing twice on the baseline and on the broken state being gone, with the expected state in its place, twice on a running patched app. | "Confirmed: The baseline reproduces twice and the patched build resolves it twice." Measure the baseline: "If the symptom does not appear twice on the baseline, there is no baseline. Do not claim that the fix works." Measure the patched build: "Confirm that the broken state is gone.", "Confirm the expected state appears.", "Do not stop at compilation or tests. The after result must come from a running patched app." |
| Where both builds were measured, the baseline and patched measurements use the same environment and data, the same UI path, and the same state check. | Protect the working tree: "Build and environment inputs shared by both runs". Measure the patched build: "Build and run the pull request or fix commit with the same environment and data.", "Run the same UI path.", "Capture after recording, screenshot, and the same state check." The condition "Where both builds were measured" covers the Inconclusive path "the patched app cannot run" and a baseline that does not reproduce (amendment 15.3). |
| The existing artifact is unedited, and no competing patch and no other pull request exists from the run. | Lead: "The existing artifact owns the fix. Verify it. Do not edit it, author a competing patch, or open another pull request." Outcome subsections: "Open no pull request.", "Open no competing pull request." |
| The repository is back in its prior state, with no user change overwritten and no user work discarded. | Protect the working tree: "Use an isolated worktree or another clean checkout when the repository supports it. Do not overwrite user changes." Cleanup: "return the repository to its prior state without discarding user work". |

Headings whose text changed:

- "## Outcomes" became "### Verification outcome (under ## Outputs)". The upstream section lists the three verdicts of a verification and what to report for each. It is not the Framework's Outcomes, and the profile reserves that heading (section 5, Colliding words).

Places where meaning, force, or scope differs from upstream:

- The dependency items "The working tree is protected before either build is measured." and "The verification outcome is chosen after the measurements and is reported before Cleanup." state orders that upstream gives only by the position of its sections. Reason: Without a listed-order default (amendment 15.2), the position of these sections would otherwise be lost. Each item rests on a use of an earlier result, not on position alone.

Order dependencies stated under Constraints, with the reason for each:

- No listed-order default. Upstream numbers no section and no paragraph that became a Task.
- The numbered actions under a Task are worked in the order listed. Reason: upstream numbered the two inner lists (Measure the baseline, Task 3, items 1 to 6; Measure the patched build, Task 1, items 1 to 5), and later items use earlier results ("Reset and repeat it.", "the same state check").
- The artifact is qualified before either build is measured. Reason: the baseline is derived from the artifact ("For an open pull request, use its base branch as the baseline.", "For a merged fix, use the revision immediately before the fix").
- The working tree is protected before either build is measured. Reason: the earlier Tasks set up the checkout and record the inputs that the builds change or share ("Use an isolated worktree or another clean checkout ... Do not overwrite user changes.", "Build and environment inputs shared by both runs").
- The baseline is measured before the patched build, which repeats the same UI path and the same state check. Reason: the patched measurement uses results of the baseline, and the baseline is the gate for any claim ("If the symptom does not appear twice on the baseline, there is no baseline.").
- The verification outcome is chosen after the measurements and is reported before Cleanup. Reason: each outcome is defined by what the measurements showed, and upstream places the outcome section before Cleanup.
- "In Measure the baseline, the baseline revision is chosen before the baseline app is brought up." Reason: bringing up the baseline app uses the revision that the two Tasks before it choose.

State-changing or external effects the work can have, with the condition upstream states:

- Create an isolated worktree or another clean checkout and build two revisions. Conditions: when the repository supports it; do not overwrite user changes.
- Bring up and drive the baseline and patched apps through the configured control adapter, and capture recordings, screenshots, and state checks.
- Mark operations status (verified, or reproduced but not fixed) and link the artifact.
- Post one concise reply in the source thread for a Confirmed outcome. Condition: after the source preflight.
- Post the normal confirmed-repro source update for an Insufficient fix outcome. Condition: only if the run has not already used it.
- For an Inconclusive outcome, post nothing in the source thread unless a direct question requires an answer.
- Never edit the existing artifact, author a competing patch, or open another pull request, on any outcome.
- Stop both builds, remove temporary profiles and captures according to retention policy, and return the repository to its prior state. Condition: without discarding user work.

Also: 5 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md`

Unchanged from upstream.

## `automations/benny/skills/triage-issue-reports/references/routing.example.md`

Unchanged from upstream.

## `automations/benny/skills/reproduce-and-fix-issues/references/feature-map.example.md`

Unchanged from upstream.
