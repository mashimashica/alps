# Make sure the handover was understood

Create an Agent Skill that helps colleagues establish shared understanding during an operational handover. A later fresh assistant will use it with an oral exchange represented as conversation or a speaker-attributed transcript. Design the Skill; do not conduct or complete the handover in this assignment.

At the fictional Lumen Demo Studio, Maya is leaving for the afternoon and Eli is taking over preparation of two demonstration kits. Both are busy and tend to use short phrases such as “that one,” “the usual time,” and “Sam might handle it.” They want to avoid discovering later that each person understood a different owner, deadline or remaining job. A polished summary alone is not enough if it conceals uncertainty or has never been confirmed by the people concerned.

This short, public example illustrates their setting. All times refer to the same local working day:

> Maya: Both kits go with the courier. Collection is the usual four o'clock. Aster is checked; put its charger in before you seal it. Birch needs the spare HDMI adapter tested.
>
> Eli: I'll pack Aster and test Birch's adapter. Are you doing the labels?
>
> Maya: I asked Sam if they could. They haven't replied. And correction: the courier moved collection to 15:30. The kits need to be at reception by 15:10.
>
> Eli: Aster packing and Birch's test are mine; reception by 15:10. If Birch fails, can I send it without the adapter?

The studio's stated constraint is that an incomplete kit cannot be dispatched without Maya's explicit approval; no one else in this exchange has that authority. Sam is not present. The example stops where the available evidence stops. Later use can include further replies, interruptions or corrections, and must not depend on this exact conversation or these kit names.

The colleague needs help expressing what they believe has been agreed, noticing consequential gaps or mismatches, and checking them with the appropriate person in ordinary conversation. Ownership of a question is not the same as ownership of the work; a suggestion is not an acceptance; a read-back is not evidence that the other person confirmed it. If there is no further reply, the assistant should still be useful without manufacturing closure. It should allow a later correction to change the understanding.

The public input interface is the conversation itself, optionally accompanied by local plain-text excerpts and explicitly supplied operational facts. Excerpts identify speakers and preserve their order; if recording, speaker identity or coverage is uncertain, that limitation is supplied or can be raised. No audio-processing service, task system or handover form is assumed. Nothing must first be converted into a fixed document. The assistant may formulate a spoken response or a question for the current user, but must not contact an absent colleague, claim to have performed the kit work, or treat a proposed action as completed. Later evidence and user replies are synthetic; no actual dispatch or messaging occurs.
