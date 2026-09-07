---
name: handover-alignment
description: Establish and update shared understanding during an operational handover from a conversation or speaker-attributed transcript. Extract owners, deadlines, remaining work, dependencies, and authority; expose consequential ambiguity and draft spoken checks without inventing agreement, completion, or contact with absent people.
---

# Purpose

Use this skill when someone needs to understand what an operational handover actually establishes, what remains uncertain, and what should be checked in ordinary conversation. The input may be the conversation itself, an ordered transcript, local plain-text excerpts, or explicitly supplied operational facts. Do not require the user to turn it into a form first.

The result is a useful current picture plus the smallest set of spoken questions that could align it. It is not a handover record, task system, dispatch decision, or proof that work was performed.

Treat a transcript or excerpt as supplied text. Do not infer unseen audio, fill gaps from presumed recording coverage, or invoke an audio-processing service.

# Read the evidence before summarizing

Process the exchange in speaker order. Keep the source speaker and, when useful, the exact short phrase that supports each material claim. Track each item or job with these fields:

- action or expected result, including the object it concerns;
- proposed, accepted, assigned, or unknown owner;
- deadline, timing, destination, sequence, and any relative-time wording;
- prerequisite, dependency, completion evidence, or failure condition;
- exception or approval authority;
- source speaker, turn/order, and confidence or limitation;
- consequence if the item is wrong or left unresolved.

Also record supplied facts separately from conversational evidence. A supplied fact may establish a rule or operating constraint, but it does not prove that participants agreed to it.

Do not silently resolve words such as “that one,” “the usual time,” “they,” “might,” or “someone.” Preserve the ambiguity and say what referent, time, person, or condition is missing. Relative times can be normalized only when the exchange explicitly establishes the relevant working day and time basis; otherwise ask.

If attribution, transcript coverage, or recording quality is uncertain, carry that limitation into the result and check the affected claim. Do not infer an omitted reply.

# Distinguish the states of a claim

Use plain labels internally or in the response so the reader can tell evidence from inference:

- **stated**: a speaker says a fact, rule, assignment, timing, or condition;
- **self-accepted**: a person says they will do the work. This shows their commitment, not that another person confirmed the shared understanding;
- **assigned**: one person names another as owner. It is not acceptance by the assignee;
- **proposed**: language such as “could,” “might,” “should,” or a question. It is not an agreed action;
- **read-back**: a participant restates their understanding. It is evidence of that participant’s view, not confirmation by the other person;
- **confirmed**: the relevant person explicitly acknowledges, agrees, or corrects the point. A read-back becomes shared confirmation only after that response;
- **completed**: explicit evidence says the action happened. Future tense, an intention, or a read-back never proves completion;
- **uncertain or conflicted**: the source is ambiguous, attribution is limited, or credible turns disagree;
- **superseded**: a later explicit correction replaces an earlier value for the affected field. Retain the old source as superseded rather than blending both values.

Do not turn a question about who will do something into ownership of the work. Track the owner of the question separately when that matters. Do not treat a person’s silence as acceptance, and do not treat a person’s suggestion as authorization.

# Build the current understanding

For each operational item, state the narrowest defensible understanding. Keep known values, unknown values, and conflicts visible. A compact entry may say:

`Item — action/result; owner: [state]; due/route: [state]; prerequisite or exception: [state]; evidence: [speaker/turn]; status: [label].`

Then identify the few unresolved points that could cause a wrong owner, missed deadline, unsafe or incomplete delivery, duplicate work, or an unauthorized exception. Rank those checks by consequence and time pressure, not by the order in which the transcript mentioned them. Typical high-impact checks include:

1. who owns each remaining action and whether that person accepted it;
2. the current deadline, handoff location, sequence, and any corrected time;
3. whether a prerequisite or quality check is complete;
4. what happens on failure or missing material;
5. who has authority to approve an exception or release an incomplete result;
6. whether an external person or dependency has actually replied.

If an unresolved point is safe to leave pending, label it pending rather than manufacturing closure. If an explicit rule assigns approval to one person, direct that question to that person; another participant’s willingness cannot substitute for the authority.

# Speak for alignment

Offer a short natural-language read-back followed by targeted checks. Use the current user’s role and the conversation’s terminology, but do not pretend to contact anybody. Address each question to the person who can answer or authorize it:

- ask the assignee whether they accept the work when acceptance is missing;
- ask the assigning or coordinating person to confirm an owner, timing, or changed instruction;
- ask the named authority for an exception decision;
- ask the current user for a missing fact when no other reply is available.

Phrase checks so a simple reply can resolve one issue, for example: “I have X due at Y, owned by Z. Has Z accepted that, and who decides if the prerequisite fails?” Keep uncertainty explicit: “I heard ‘the usual time’; what exact time should we use?” A read-back should include only supported claims and should name any unresolved item rather than imply that the listener has agreed.

The assistant may formulate what the current user can say next. It must not send a message, call an absent colleague, fill in a handover form, or claim to have packed, tested, dispatched, or otherwise completed work.

# Apply later replies and corrections

When new conversation evidence arrives, append it in order and update only the fields it actually bears on. An explicit correction governs the current value for that field, while the earlier value becomes superseded. Recheck dependent questions: a changed deadline may change urgency; a changed owner may change who must confirm; a changed failure rule may change the required authority. Keep unresolved disagreement visible until the relevant people reconcile it. Never convert a later intention into completion.

When there is no further reply, report the best-supported current understanding, list the consequential open checks, and provide a spoken question or read-back. The absence of closure is itself part of the result.

# Recommended response shape

Use a conversational response rather than a mandatory fixed document, while making the distinctions easy to inspect:

1. **Current understanding** — concise item-by-item claims with owners, timing, dependencies, authority, and evidence status.
2. **Still open or risky** — unresolved ambiguity, conflict, missing acceptance, uncertain attribution, or unverified completion, ordered by consequence.
3. **What to say next** — a short read-back and one question per consequential gap, addressed to the appropriate person.
4. **Update rule** — if useful, state which later reply or correction would change the picture.

Do not call the handover complete unless the evidence supports the relevant confirmations. If the user asks for a polished summary, retain the open checks and status labels so polish cannot conceal uncertainty.
