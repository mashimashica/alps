# Investigation

## Purpose

Answer the user's question about the code with a cited explanation, or with a recommendation where the request is a decision between alternatives. The work is read-only and produces no code change.

## Outcomes

- The reply answers the question with a cited explanation, or with a recommendation and a tradeoffs table where the request is a decision between alternatives.
- The explanation or recommendation rests on a trace of the code the question is about.
- The investigation is read-only and leaves the code unchanged.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Trace the code the question is about. For motivation questions, also route through the **why** skill.
2. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only investigation`.
3. Produce the output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas), or a recommendation with a tradeoffs table if the request is a decision between alternatives.
4. Apply the **unslop** skill to the reply.

## Outputs

**Reply:** the investigation output. For "are we sure?" answers, include your real judgment with reasons. Push back if the premise is wrong (see Autonomy).

## Constraints

**You own the answer. Plan, route, write.**

Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change.

No PR, no babysit, no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 3 follows step 1, because the output rests on the trace.
- Step 4 follows step 3, because the reply is the output step 3 produces.
