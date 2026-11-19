---
name: ketchup-video
description: "Catch the user up like /ketchup, with a short subtitled video of slides for what happened and the waiting calls as text under it. Use for /ketchup-video."
disable-model-invocation: true
---

# Ketchup video

## Purpose

Catch the user up as ketchup does, with what happened shown in a short subtitled video of slides and the waiting calls as text under it.

## Outcomes

- Where the render succeeds, the video shows what came of each thing the user asked for, and whether it is done, still running, failed, or not checked.
- Where the render succeeds, the video is drawn only from facts you have, with no invented number and no screen you did not capture.
- Where the render succeeds, each slide's subtitle is readable when the video plays at chat size and covers nothing.
- Where the render succeeds, each slide's measured hold in the rendered file is long enough to read the words the slide adds, at least one second for each three words.
- Where the render succeeds, the action items stand in the reply as text under the video.
- Where the render fails, the reply says so in one line and gives only the calls.

## Activities & Tasks

The following Tasks are required whenever this skill runs, each with the conditions it states. Numbers identify the Tasks and set no order.

### Slides

1. Use the screenshots, recordings, diffs, and data the work produced, not the chat's prose about them.
2. Before you draw, write the one sentence the user should leave with and one line per slide. Drop each slide that does not change what the user knows. Use at most 10 slides, and fewer is better. Neither note goes in the reply.
3. Each slide makes one point. Build the slides on one picture and change it from slide to slide, rather than cut to an unrelated one. A color or shape means the same thing on every slide. Show the work in pictures, such as how a system works, a PR stack with each PR's state, a before and after of a fix, or options side by side. Point at what changed with arrows, highlights, and motion. A slide is never a bullet list, a status list, a table, or boxes with nothing connecting them.
4. Keep text to the minimum. Put each label on the thing it names, in plain words a person would say, not tags like "Tests: pass". Never caption what a picture shows, and never give a fact twice, across slides or in the text under them.
5. Show what came of each thing the user asked for, and whether it is done, still running, failed, or not checked. Never show something done that still waits on the user. Show any bug found and fixed on the way. If a visible change has no screenshot, say so on its slide and name what changed on screen. Draw only from facts you have. Never invent a number, and never draw a screen you did not capture.

### Subtitles

1. Give each slide one short subtitle line, about ten words, that says its point the way you would tell the user, from only what that slide shows. Say what the picture means rather than read out its labels.
2. Put the subtitle in a strip below the slide, the same height on every slide and empty except for the subtitle, so it never covers the slide. Set it small, but readable when the video plays at chat size.

### Render

1. Render one silent landscape video, such as an mp4, with motion between slides. Every frame is the slide itself, edge to edge, above its subtitle strip. Make the frames from the slides, never by recording a screen, and burn each subtitle into its slide's frames so it stays on screen for the slide's whole hold. Hold each slide long enough to read the words it adds, at least one second for each three words.
2. Before you embed the video, check the rendered file. Look at one frame from each slide at chat size, and check that its subtitle is readable and covers nothing. Measure each hold by matching the file's frames to the slide, not with a still-frame detector, which counts the faint ends of a fade as still. Count the words each slide adds against its measured hold. Fix any slide you cannot read in that time, render again, and check again.

## Outputs

The reply is ketchup's opening sentence, the embedded video, one line naming any work left that you can do yourself, and the action items. When the video shows a call's options, call each option by the name the video gives it. If the render fails, say so in one line and give only the calls.

## Controls

Follow [`/ketchup`](../ketchup/SKILL.md), but show what happened in a short subtitled video instead of its summary and visuals. Its window starts at the last message the user wrote before `/ketchup-video`, not before any earlier `/ketchup`.

The hold is the time a slide is fully on screen, not counting the motion into or out of it. A slide adds its subtitle and each word that was not on the slide before it, including a label it changes. The first slide adds all its words. Words inside a screenshot do not count.

## Constraints

Writing and rendering the video, outside the repo, is the one exception to ketchup's read-only rule.

These dependencies are required.

- The one sentence the user should leave with and the one line per slide are written before any slide is drawn.
- The slides and their subtitles come before the render, because the frames are made from the slides and each subtitle is burned into its slide's frames.
- The rendered file is checked before the video is embedded, and a file rendered again after a fix is checked again.
