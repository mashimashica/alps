# Verify an existing fix

## Purpose

Establish whether an existing pull request or commit resolves the reported symptom, from the baseline and the patched build running under the same conditions. Authoring or changing a fix is outside this mode.

## Outcomes

- The run reports one verification outcome, Confirmed, Insufficient fix, or Inconclusive, and it matches what the baseline and the patched build showed.
- A Confirmed outcome rests on the symptom reproducing twice on the baseline and on the broken state being gone, with the expected state in its place, twice on a running patched app.
- Where both builds were measured, the baseline and patched measurements use the same environment and data, the same UI path, and the same state check.
- The existing artifact is unedited, and no competing patch and no other pull request exists from the run.
- The repository is back in its prior state, with no user change overwritten and no user work discarded.

## Activities & Tasks

The following Tasks are required whenever this mode runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

### Qualify the artifact

1. Require one concrete artifact:

    - An open pull request with code changes that address the symptom
    - A merged pull request
    - A merged commit with matching code and intent

    A thread claim, tracker status, branch name, or cause hypothesis without a pull request or commit is not enough.

2. When several artifacts exist, choose the one linked from the source thread or tracker. Otherwise choose the closest match to the affected code and state why.

### Protect the working tree

1. Use an isolated worktree or another clean checkout when the repository supports it. Do not overwrite user changes.

2. Record:

    - Baseline revision
    - Patched revision
    - Pull request or commit URL
    - Build and environment inputs shared by both runs

3. Use regular `github.com` pull request links.

### Measure the baseline

1. For an open pull request, use its base branch as the baseline.

2. For a merged fix, use the revision immediately before the fix when that revision builds and represents the old behavior.

3. Through the configured control adapter:

    1. Bring up the baseline app.
    2. Confirm the correct app and environment.
    3. Run the reported path through real UI actions.
    4. Observe the discriminating symptom.
    5. Reset and repeat it.
    6. Capture baseline recording, screenshot, and state check.

    If the symptom does not appear twice on the baseline, there is no baseline. Do not claim that the fix works.

### Measure the patched build

1. Build and run the pull request or fix commit with the same environment and data.

    1. Run the same UI path.
    2. Repeat it twice.
    3. Confirm that the broken state is gone.
    4. Confirm the expected state appears.
    5. Capture after recording, screenshot, and the same state check.

    Do not stop at compilation or tests. The after result must come from a running patched app.

### Cleanup

1. Stop both builds, remove temporary profiles and captures according to retention policy, and return the repository to its prior state without discarding user work.

## Outputs

### Verification outcome

#### Confirmed

The baseline reproduces twice and the patched build resolves it twice.

- Mark operations status as verified.
- Link the artifact.
- Post one concise source-thread reply after the source preflight.
- Include the before and after result.
- Open no pull request.

#### Insufficient fix

The symptom appears on both baseline and patched builds.

- Mark operations status as reproduced but not fixed.
- Link the artifact and say it did not resolve the symptom.
- Post the normal confirmed-repro source update if the run has not already used it.
- Open no competing pull request.

#### Inconclusive

The baseline does not reproduce, the patched app cannot run, or the evidence does not show the discriminating state.

- Do not claim success.
- State which half could not be measured.
- Keep the result in the operations thread or run output.
- Post nothing in the source thread unless a direct question requires an answer.

## Constraints

Use this mode when an open pull request or merged commit plausibly fixes the report.

The existing artifact owns the fix. Verify it. Do not edit it, author a competing patch, or open another pull request.

Activities and Tasks may be worked in any order unless a Task or one of these dependencies states otherwise. These dependencies are required.

- The numbered actions under a Task are worked in the order listed.
- The artifact is qualified before either build is measured.
- The working tree is protected before either build is measured.
- In Measure the baseline, the baseline revision is chosen before the baseline app is brought up.
- The baseline is measured before the patched build, which repeats the same UI path and the same state check.
- The verification outcome is chosen after the measurements and is reported before Cleanup.
