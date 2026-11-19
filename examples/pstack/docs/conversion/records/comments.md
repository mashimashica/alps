# Conversion record: no-comments and the comment-sicko agent

[Conversion guide](../README.md)

## `skills/no-comments/SKILL.md`

Title: No comments. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Clear the scope of comments that do not survive Comment Sicko's fresh perspective, with the code behind each accepted flag fixed and each constraint a comment claimed encoded or reported open.

| Outcome | Basis in the upstream text |
| --- | --- |
| No application-code edit, scope escape, or exception-protected deletion by Comment Sicko stands. | Step 2: "Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, ...", "Revert and rerun one rejected report with the failure named.", and "Restore deletions only with exact exceptions and scoped proof." Worded as what stands at the end, so that it holds whether a rejection reverts the whole report or one item (see findings). |
| No accepted flag misstates its `MUST KILL` reason or treats kept intentional code as guilty. | Step 2: "Reject ... misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty." Step 3 acts only on "accepted flags" and "the accepted set". |
| Every restored deletion has an exact exception and scoped proof. | Step 2: "Restore deletions only with exact exceptions and scoped proof." Supported by "Do not restore those comments." and "If a kill is ambiguous, do not restore." |
| Every keep that is refuted or still ambiguous is deleted. | Step 2: "If a keep is refuted or still ambiguous, delete it." |
| Every correctness or safety suppression among the scope's lint and TypeScript suppressions, including any Comment Sicko missed, stays an actionable `MUST KILL`. | Step 2: "Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s." |
| Every reshape flag on an our-code surprise stays actionable. | Step 2: "Reshape flags on our-code surprises stay actionable." Stated beside the suppression Outcome because step 2 insists on both in parallel, and the reject list of step 2 ("flags that treat kept intentional code as guilty") could otherwise remove these flags without any Outcome failing. "Do not restore those comments." is covered by the Outcome on restored deletions, since an our-code surprise has no keep-list exception. |
| Every accepted flag has its smallest root-cause fix in scope, or, where the root cause is out of scope, the smallest in-scope fix with the rest reported open. | Step 3: "Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API." Step 4: "Implement the smallest root-cause fix in scope. ... If the root cause is out of scope, land the smallest in-scope fix and report the rest open." The alternative ending is upstream's own. |
| Every named workaround is removed. | Step 4: "Remove every named workaround." Stated on its own because upstream states it unconditionally, on both the in-scope and the out-of-scope path, and it is judged apart from the fix. |
| Each constraint comment that is not a keep about things we cannot change is deleted. | Step 5: "Leave keeps about things we cannot change. ... If approved, encode then delete. Otherwise delete ...". The comment comes out on both paths. |
| Each constraint such a comment claimed has an offer of the cheapest in-scope type, runtime, test, or CI lint. | Description: "offer encodings for claimed constraints". Step 5: "Offer the cheapest in-scope type, runtime, test, or CI lint.", stated without condition. Step 6 reports "encoding offers". The approval conditions of step 5 govern the encoding, not the offer, so the Outcome holds on the interactive, unattended, and eval paths. Stated apart from the encoding Outcome because a run can make the offer and still not encode. |
| Each constraint such a comment claimed is encoded where approval was given, and otherwise reported open with the out-of-scope work sketched. | Step 5: "Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval. Unattended and eval require caller pre-approval. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work." |
| The report names the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work. | Step 6: "Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work." Also "report it open" (step 2), "report the rest open" (step 4), "report the constraint open" (step 5). |

Headings whose text changed:

- "## Steps" became "## Tasks". Only element names are allowed as H2 headings, and upstream has a single numbered list (profile section 5). No file cites the heading "Steps". "Step 4" inside step 3 resolves through the unchanged numbers and the governing sentence ("pstack text refers to them as steps").

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before step 2. Reason: step 2 uses a result only step 1 produces ("Inspect its report and diff.").
- Step 2 before steps 3 to 5. Reason: step 2 is the verdict the later steps act on. Lead line "Act on accepted findings."; step 3 "Fix trivial accepted flags", "the accepted set"; step 5 "Leave keeps about things we cannot change", which are the keeps that survive step 2.
- Step 3 before step 4. Reason: upstream allocates the two steps in words ("Stop at the sketch. Architect shapes. Step 4 implements."), and step 4 implements the sketch only step 3 produces.
- Step 6 last. Reason: it reports results only steps 1 to 5 produce (deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, other open work).
- Kept inside their steps, not lifted: the rerun loop of step 2 ("Revert and rerun one rejected report", covered by "Unless a Task states otherwise"), "Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, trace their symbol or run `/why` on it" (step 2), and the approval gate and "encode then delete" of step 5.

State-changing or external effects the work can have, with the condition upstream states:

- Step 1 spawns Comment Sicko, which deletes comments and suppressions in the scope's files in the working tree. No approval is stated. Step 2 inspects the report and diff afterwards.
- Step 2 reverts the edits of a rejected report ("Revert and rerun one rejected report with the failure named"). Condition: the report is rejected. No approval and no way of reverting is stated.
- Step 2 restores deleted comments. Condition: "only with exact exceptions and scoped proof".
- Step 2 deletes a keep. Condition: "If a keep is refuted or still ambiguous".
- Steps 3 and 4 edit code in scope (delete a dead path, drop a parameter, use the real API, implement the smallest root-cause fix, remove every named workaround, "land the smallest in-scope fix"). Limits: in scope only ("Neither authorizes widening the fence nor fixing instances outside it"), "Never bolt on symptom guards". No approval is stated.
- Step 5 adds an encoding (type, runtime, test, or CI lint). Approval: "Wait for interactive approval. Unattended and eval require caller pre-approval."
- Step 5 deletes constraint comments, whether or not the encoding is approved ("If approved, encode then delete. Otherwise delete"). Exception: "Leave keeps about things we cannot change."
- No commit, push, merge, deploy, posted message, or write outside the repository is stated. `/why` and `/architect` read and sketch only.

Also: 4 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `agents/comment-sicko.md`

Title: Comment Sicko. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Rid the scope of every comment that the keep list does not protect and identify refactor targets, without touching the code.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every comment that remains in the scope falls under a keep-list exception that clearly applies. | "Only these exceptions get to crawl away." and "That list is my only leash. When I am not sure a keep clause applies, the comment dies. Everything else is meat." |
| A comment that carries `IMPORTANT`, `do not remove`, `too risky`, `fine for now`, or a long justification remains only where it is a foreign keep-list gotcha proven true today on a live path. | "`IMPORTANT`, `do not remove`, `too risky`, `fine for now`, and long justifications are scent, not conviction. ... Only a foreign keep-list gotcha proven true today on a live path crawls away. ... Doubt after the hunt is meat." |
| Every killed comment on a surprise in our own code, every killed suppression whose rule catches real bugs or protects correctness or safety, and every killed long justification has its exact symbol marked `MUST KILL`. | Keep-list bullet 2: "Surprises in our own code are meat. Kill them and mark the exact symbol `MUST KILL` for rename, extract, type, or rearchitecture ...". Suppression paragraph: "If it catches real bugs or protects correctness or safety, kill the suppression and mark the exact guilty symbol `MUST KILL`." Long-justification paragraph: "Kill it. ... Mark the exact guilty symbol `MUST KILL`." |
| Every flag names code inside the scope and tells the truth. | "Every flag names code inside the scope and tells the truth. I invent nothing." The rule is stated once, here. Constraints keep only "Invent nothing." |
| The report names the touched files, the deletion count, each `MUST KILL` flag with one line, and the skips. | "Report only. Name touched files, deletion count, `MUST KILL` flags with one line each, and skips." no-comments step 2 inspects "its report and diff". |

Carried from the frontmatter description into the body:

- "A deranged comment-hater that savors deletion and condemns workaround code." This is persona text, not a rule. Profile section 8 prescribes the Enablers statement, and its words "a comment-hater that savors deletion and condemns workaround code" come from this description. The upstream body has only "I hate comments." The word "deranged" stays in the frontmatter only, as the profile's wording has it.

Upstream wording not carried over:

- First-person voice throughout ("I", "me", "my") Reason: Persona narration. Profile section 8 addresses the body to the performing agent. Every rule is restated as an instruction or a stated rule.
- "Feed me" (twice) Reason: Persona figure. The scope it names is in Inputs.
- "commented-out corpses", "workaround sermons", "I want them all." Reason: Persona figures. Carried as "commented-out code", "workaround explanations", and "alike" in step 1.
- "get to crawl away", "crawls away" Reason: Persona figure for a kept comment. Carried as "are kept" and "Keep only".
- "are meat", "is meat" (three times), "the comment dies", "die" Reason: Persona figures for deletion. Carried as "are not kept", "Delete every comment ...", "delete the comment", and "are killed".
- "That list is my only leash." Reason: Persona figure that repeats "Only these exceptions get to crawl away." Stated once in Controls.
- "stink" Reason: Persona figure. Carried as "Treat them as suspect."
- "are scent, not conviction" Reason: Persona figure. Carried as "a scent to follow, not a verdict". The word "scent" is kept.
- "the hunt" Reason: Persona figure for the reading and tracing. Carried as "after that".
- "is a confession" Reason: Persona figure. Carried as "It is an admission of guilt."
- "Never polish meat into a shorter alibi." Reason: Persona figures "meat" and "alibi". The prohibition is carried at its upstream reach as "Never polish a comment that must be deleted into a shorter justification.", since "meat" stands for any comment that must die.

State-changing or external effects the work can have, with the condition upstream states:

- Deletes comments and suppressions in the files of the scope, in the working tree it is spawned in. Conditions: the comment is not protected by the keep list, and "When it is unclear whether a keep clause applies, delete the comment." No approval is stated. The caller (no-comments step 2) inspects the diff afterwards and can revert it.
- Limits upstream states: "Do not touch the code", "Never write application code", every flag inside the scope.
- Runs `/why` from the **why** skill on a symbol or call, which reads commits and PR discussions and changes nothing.
- No commit, push, merge, posted message, or write outside the scope is stated.

Also: 13 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
