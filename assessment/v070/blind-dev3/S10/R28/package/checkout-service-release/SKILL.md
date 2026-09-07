---
name: checkout-service-release
description: Release an approved checkout-service candidate in a supplied simulation, from candidate inspection and qualification through promotion and post-promotion health and checkout evidence. Use when a request names an exact candidate and target environment and the release tool and state file are available.
---

# Checkout service release

Perform the release as an evidence-based, candidate-specific workflow. The supplied `release_tool.py` is a local simulation; invoke it as:

```sh
python3 <environment-path>/release_tool.py --state <state.json> <operation>
```

The caller must provide authorization for simulation operations. Do not access external repositories, deployment services, or customer state, and do not invent approval or substitute a candidate.

## Establish the release basis

Read `inspect` before making decisions. Confirm from its returned state the requested candidate ID, its current digest, the target environment, service owner, qualification record, and approval record. Treat a changed candidate digest as a new candidate for all release purposes.

Qualification and approval are separate conditions. Run:

```sh
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate CANDIDATE_ID
```

Qualification must pass for the exact current candidate digest. It records a sequence and does not approve the candidate. A usable owner approval must match the candidate ID and digest, name the configured service owner, and have a qualification sequence later than the recorded qualification sequence. If any required approval is absent or mismatched, stop before promotion; you may still inspect, qualify, and prepare an assessment.

## Promote only the qualified, approved candidate

After qualification and the matching subsequent approval are observed, promote using a stable request ID supplied or chosen for this release attempt:

```sh
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate CANDIDATE_ID --request-id REQUEST_ID
```

A successful response is evidence of the tool result, not complete release success. If the command exits with a timeout or otherwise leaves the effect uncertain, do not repeat `promote` blindly. First query:

```sh
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id REQUEST_ID
```

Use the same request ID for an exact retry only when status shows no completed effect and the candidate and digest still match; if state changed, inspect again and re-check all gates. Never reuse a request ID for another candidate.

## Judge production outcome

After promotion (or after confirming its effect), run both checks:

```sh
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

The health probe must report the promoted revision healthy, and checkout must report completion for that same production revision. A successful promotion, healthy probe alone, or command exit code alone does not establish the intended release outcome. If either check fails, report the observed revision and failure and identify follow-up; do not claim the release succeeded.

## Report

Return a concise assessment that distinguishes:

- observed candidate ID, digest, qualification result and sequence;
- approval basis and whether it matched the exact qualification;
- promotion result, request ID, and any uncertain effect;
- production revision, health result, and checkout result;
- requirements satisfied, unmet, or unconfirmed; and
- required follow-up.

Keep tool output and your judgment separate. Preserve command errors and nonzero outcomes as evidence. Do not perform a future business instance merely to demonstrate the skill.
