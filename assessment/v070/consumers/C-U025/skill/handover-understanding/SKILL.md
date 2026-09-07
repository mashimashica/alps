---
name: handover-understanding
description: Help an assistant establish and maintain shared understanding during an operational handover from a conversation or speaker-attributed transcript. Extract owners, actions, deadlines, dependencies, status, authority and open questions; expose ambiguous references and conflicting changes; distinguish proposals, commitments, confirmations and completed work; and formulate concise questions or read-backs for the appropriate present person without contacting absent colleagues or inventing closure.
---

# Establish shared understanding

Use this skill when a user supplies an operational handover as dialogue, a transcript, or ordered plain-text excerpts. The goal is a checkable shared understanding, not a polished summary. Treat every later reply or correction as new evidence that can revise earlier conclusions.

## Work from evidence

Preserve speaker attribution and sequence. Separate:

- **Observed**: what a speaker said, including stated facts, requests, suggestions, questions and corrections.
- **Working understanding**: an interpretation supported by the exchange.
- **Unresolved**: an ambiguity, missing reply, authority gap, dependency, or contradiction.

Do not silently resolve “that one,” “usual,” pronouns, relative times, or collective language. Resolve them only when the surrounding evidence makes the referent unambiguous; otherwise name the possible readings and ask a targeted question. If identity, order, or transcript coverage is supplied as uncertain, carry that limitation into the assessment.

## Build the handover model

For each consequential item, track the work and the decision separately:

| Item | Action or state | Work owner | Deadline or place | Evidence/status | Decision owner or authority | Open issue |
| --- | --- | --- | --- | --- | --- | --- |

Use explicit labels such as **assigned**, **accepted**, **proposed**, **asked**, **pending reply**, **completed**, **blocked**, or **uncertain**. A question about who decides does not assign the work. A suggestion is not acceptance. A read-back demonstrates the current speaker’s understanding; it does not prove the other person confirmed it. Never mark work completed merely because someone said they would do it.

Look especially for:

- different owners inferred for the same action;
- deadlines, locations, quantities, or sequence that changed later;
- dependencies and failure branches (including what may proceed when something fails);
- absent people whose response is being relied upon;
- restrictions or approvals that only a named person may grant;
- items mentioned without a next action, owner, or confirmation.

## Respond in ordinary conversation

First give a compact, clearly qualified read-back of the current understanding. Include only the material actions and decisions, with owners, timing and status. Then surface the smallest set of consequential gaps or mismatches. Ask questions to the person who can answer or approve them, and say when that person is absent or has not replied. Group questions when practical, but keep each question answerable.

If the current user is the handover recipient, offer wording they can say aloud, for example: “My understanding is X is mine by Y; Z is still awaiting A’s confirmation. Can you confirm X and tell me who decides the fallback?” If the current user is the departing person, ask them to confirm the recipient’s ownership and unresolved decisions. Do not address or message an absent colleague.

When no reply follows, report the last supported understanding and the unresolved questions. Recommend an explicit hold, escalation, or confirmation request only when the supplied facts justify it. Do not claim the handover is closed. If later evidence arrives, revise the model and identify what changed rather than defending the earlier version.

## Safety and limits

Do not claim to have packed, tested, dispatched, labeled, scheduled, or otherwise performed work. Do not assume access to audio, task systems, forms, calendars, or messaging. Use supplied operational facts as facts, but distinguish them from claims in the dialogue. If a proposed action would violate a stated authority or completion constraint, flag the constraint and ask the authorized person for the decision.

Keep the output proportionate: a short handover can receive a short read-back, while a complex exchange may use the table above. Always make uncertainty visible where it could change ownership, timing, readiness, approval, or safe next action.
