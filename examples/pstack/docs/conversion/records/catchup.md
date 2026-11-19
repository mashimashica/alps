# Conversion record: ketchup, ketchup-video

[Conversion guide](../README.md)

## `skills/ketchup/SKILL.md`

Title: Ketchup. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Catch the user up on what changed in this chat since the last message they wrote before `/ketchup`, so that they understand each change, not only where it stands, and can make every call waiting on them from the reply alone. Notifications and subagent results are not their messages.

| Outcome | Basis in the upstream text |
| --- | --- |
| The reply tells what came of each thing the user asked for, and whether it is done, still running, failed, or not checked, or, where nothing happened and nothing waits on the user, it says so. | Write the reply, step 3 (upstream paragraph 3): "Then sum up in one short bullet per thing the user asked for: what came of it, and whether it is done, still running, failed, or not checked." Opening paragraph: "help them understand each change, not only where it stands". The alternative ending, with its condition, is Write the reply, step 2 (upstream paragraph 2): "If nothing happened and nothing waits on the user, say so and stop." |
| The reply lists every action item still waiting on the user, even one raised before their last message. | Opening paragraph: "Then lay out every call waiting on them". Gather what changed, paragraph 2: "Include any still waiting on the user, even one raised before their last message." Write the reply, paragraph 1: "Never cut items or shrink them to stay under a word count: no count in place of a list, and no link in place of an item." Paragraph 4: "Then list the action items." Description: "List every item waiting on them". |
| The reply holds no call made up to fill it. | Gather what changed, paragraph 2: "Never make up a call to fill the reply." Split from the completeness Outcome because the two results can fail apart (Framework section 2). |
| The reply alone is enough to decide each call, with "unknown" written for a fact the call needs that is not known. | Opening paragraph: "so they can make it from your reply alone". Write the reply, step 1 (upstream paragraph 1): "A link can add depth, but the reply alone must be enough to decide." Description: "with what they need to decide it from the reply alone". The "unknown" path is Gather what changed, paragraph 3: "Write \"unknown\" for a fact the call needs that you do not know." |
| Every state, number, and picture in the reply matches the facts it comes from, which for a PR, CI run, or agent this chat touched means its current state. | Gather what changed, paragraph 1: "Check the current state of each PR, CI run, or agent this chat touched. Check each number you will show against the facts it comes from, and say so when you correct one." Write the reply, paragraph 3: "Each line must stay true when read alone. Never mark something done that still waits on the user". Visuals, paragraph 4: "Draw diagrams and charts from facts you have", "Never invent a number, and never draw or generate a picture of a screen you did not capture." |
| Every fact in the reply makes sense to a user who remembers their last message and nothing after it. | Opening paragraph: "Assume the user remembers their last message and nothing after it." Second paragraph: "Call each PR, branch, or agent by a name the user would know, not by a label you invented. If a fact needs context to make sense, give the context or leave the fact out." "in plain words" is not part of the Outcome, because the voice rules let the reply carry a hash, path, command, or count the user needs to act, and require the number or link of each PR, issue, or agent a call is about. The voice rules stay whole under Controls. |
| Each visible change has its screenshot or video embedded inline, or its summary line is marked "No screenshot yet," and says what changed on screen. | Visuals, paragraph 4: "Embed screenshots and videos inline when the change is visible, not only as links. If a visible change has none, mark its summary line \"No screenshot yet,\" and say there what changed on screen." Write the reply, paragraph 3: "Embed inline the screenshots and videos the work produced". Description: "and small visuals". |

Order dependencies stated under Constraints, with the reason for each:

- dependency: What changed is gathered and checked before the reply is written.; reason: Result use and order word: the reply's action items are written from what "For each item, collect ..." gathers, its states from "Check the current state ...", and its numbers are checked under "Check each number you will show" (future "will show"). Upstream sections are in that order.

State-changing or external effects the work can have, with the condition upstream states:

- None permitted. The turn changes no code, starts no app or job, and posts nothing. Condition upstream states: Prohibition, no exception in this file: "Keep this turn read-only. Make visuals only from what you already have: do not change code, start an app or a job, or post anything."
- Makes visuals for the reply: a Mermaid diagram, a chart or diagram from `/visualize`, or a generated image. Condition upstream states: Condition: "only from what you already have" and "from facts you have". No approval stated. Upstream does not say whether making one writes a file, or where.
- Reads the current state of each PR, CI run, or agent this chat touched. This is a read, not a change. Condition upstream states: No approval stated.

Also: 10 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/ketchup-video/SKILL.md`

Title: Ketchup video. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Catch the user up as ketchup does, with what happened shown in a short subtitled video of slides and the waiting calls as text under it.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where the render succeeds, the video shows what came of each thing the user asked for, and whether it is done, still running, failed, or not checked. | Opening paragraph: "show what happened in a short subtitled video instead of its summary and visuals". Slides, paragraph 4: "Show what came of each thing the user asked for, and whether it is done, still running, failed, or not checked." The condition comes from "If the render fails, say so in one line and give only the calls." |
| Where the render succeeds, everything the video shows comes from facts the work has, with no invented number and no drawn screen that was not captured. | Slides, paragraph 4: "Draw only from facts you have. Never invent a number, and never draw a screen you did not capture." Slides, paragraph 1: "Use the screenshots, recordings, diffs, and data the work produced, not the chat's prose about them." Restated with the video as subject (profile section 5). |
| Where the render succeeds, each slide's subtitle is readable when the video plays at chat size and covers nothing. | Subtitles: "Put the subtitle in a strip below the slide ... so it never covers the slide. Set it small, but readable when the video plays at chat size." Render, paragraph 2: "Look at one frame from each slide at chat size, and check that its subtitle is readable and covers nothing." |
| Where the render succeeds, each slide's measured hold in the rendered file is long enough to read the words the slide adds, at least one second for each three words. | Render, paragraph 1: "Hold each slide long enough to read the words it adds, at least one second for each three words." Render, paragraph 2: "Measure each hold by matching the file's frames to the slide", "Count the words each slide adds against its measured hold. Fix any slide you cannot read in that time, render again, and check again." |
| Where the render succeeds, the action items stand in the reply as text under the video. | Opening paragraph: "The reply is ketchup's opening sentence, the embedded video, one line naming any work left that you can do yourself, and the action items." Description: "the waiting calls as text under it". Slides, paragraph 3: "the text under them". |
| Where the render fails, the reply says so in one line and gives only the calls. | Opening paragraph: "If the render fails, say so in one line and give only the calls." |
| On either path, the action items and calls in the reply meet ketchup's Outcomes for them. | Opening paragraph: "Follow [`/ketchup`]\(../ketchup/SKILL.md), but show what happened in a short subtitled video instead of its summary and visuals." The video replaces only the summary and visuals, so ketchup's rules for the action items still hold. "The reply is ... and the action items." and "If the render fails, say so in one line and give only the calls." name them on both paths. The Outcome refers to ketchup's Outcomes (its Outcomes 2 to 4) without copying them. ketchup is named plainly, as upstream does in "ketchup's opening sentence", so the generator's classification is unchanged (checked with checks/classify.mjs). |

Carried from the frontmatter description into the body:

- "the waiting calls as text under it". The body gives the reply's parts in order ("the embedded video, one line naming any work left that you can do yourself, and the action items") and speaks of "the text under them", but never says the calls are text under the video. The phrase is carried in the description's words into the Purpose, and Outcome 5 states it as a result.

Order dependencies stated under Constraints, with the reason for each:

- dependency: The one sentence the user should leave with and the one line per slide are written before any slide is drawn.; reason: Order word: "Before you draw, write the one sentence the user should leave with and one line per slide."
- dependency: The slides and their subtitles come before the render.; reason: Result use: "Make the frames from the slides, never by recording a screen, and burn each subtitle into its slide's frames". The render uses what only Slides and Subtitles produce.
- dependency: The rendered file is checked before the video is embedded, and a file rendered again after a fix is checked again.; reason: Order word and gate: "Before you embed the video, check the rendered file." and "Fix any slide you cannot read in that time, render again, and check again." The check is the gate for embedding.

State-changing or external effects the work can have, with the condition upstream states:

- Writes the slides, the frames, and the rendered video file, outside the repository. Condition upstream states: Stated as a permission with a bound: "Writing and rendering the video, outside the repo, is the one exception to its read-only rule." No approval stated. No location outside the repo is named.
- Nothing else. Through "Follow `/ketchup`" the turn changes no code, starts no app or job, and posts nothing. Condition upstream states: ketchup's read-only rule, by reference.

Also: 9 statements moved to the section their function calls for; 4 additions other than the Purpose and Outcomes (fixed sentences, pointers).
