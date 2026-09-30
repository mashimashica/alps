# Operations

How this team runs the Processes of the service-change model. People read it, and so does the agent that the harness wakes on a schedule. It is guidance, not a workflow: the Processes have no fixed order, and whoever decides what to run next weighs this guidance against the current Artifacts and their evaluations.

## What comes first

- Clarify a change before designing for it. Run Requirements Clarification when stakeholder information or an improvement proposal is new or has changed, and Feasibility Assessment once its change brief has settled. Solution Design starts from a settled change brief.
- Measure a release candidate in the pilot (Pilot Measurement) before assessing it (Service Change Assessment), and make the Production Release Decision on the pilot assessment of that same candidate.
- Production Release follows a change request that approves exactly the candidate that was checked. A new candidate invalidates the earlier checks and approval: measure, assess, and decide again.

## What takes priority

- Production comes first. When new production observations show an effect on users or a missed service level objective, run Incident Response before starting other work.
- Next come the changes that are already in the pilot or awaiting a release decision, before work on new changes.
- When production observations accumulate after a release, run Change Retrospective for that change, so that what was learned reaches the next change as an improvement proposal.

## When not to run a Process

- Do not run Production Release without a change request that names the candidate, or other than through the authorized release job that the production policy requires.
- Do not run a Process again when its inputs have not changed since its last run was judged, unless the evidence of that evaluation is stale or someone asked for it.
- Do not judge an Outcome achieved because a run succeeded or an output exists; leave it unverified until its evidence has been read.
- Leave the decisions that need the service owner's approval to the service owner, and report what waits for them.
