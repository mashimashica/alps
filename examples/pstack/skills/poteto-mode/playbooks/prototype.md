# Prototype

## Purpose

Make a design decision cheaply, with a throwaway prototype as the instrument. The real build is not part of this work.

## Outcomes

- The decision the prototype exists to make has a recommendation with the alternatives and their tradeoffs, or the work is routed to Feature because there is no decision to make.
- The evidence for each variant is an observation on the matching surface, screenshots for a visual decision and the observed output or timing for a behavioral one.
- The prototype code sits in an isolated scratch dir, separate from production source.
- The prototype is presented as throwaway, not as shippable code.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Scope the decision the prototype exists to make: which layout, which interaction, which density, or for an empirical fork which behavior, timing, or approach. No decision means no prototype. Route to Feature.
2. Gather references when the design space is open. Search for prior art, summarize a moodboard of themes, palettes, and layouts, let the user pick directions before building. Skip when the direction is set.
3. Build throwaway in an isolated scratch dir, separate from production source. For a visual decision, vanilla HTML/CSS/JS or the lightest stack that renders the idea, CDN deps, a dev server with hot reload. For a behavioral or timing decision, the smallest script that exercises the question. No production framework, no tests, no abstractions.
4. When comparing alternatives, build them behind one switcher (buttons or a keypress), each variant labeled. This is the **exhaust-the-design-space** principle skill made cheap.
5. Verify on the matching surface. For a visual decision, screenshot each variant via the control skill and drive the interaction. For a behavioral or timing decision, observe the thing you are deciding by logging the timing, printing the output, or watching the render. The observation is the test here, not an assertion.
6. Present alternatives, tradeoffs, and a recommendation. The output is the decision plus the throwaway artifact, not shippable code. Hand the chosen direction to **Feature** (or `architect` for the shape) for the real build.

## Outputs

**Reply:** the variants explored, the evidence (screenshots for a visual decision, the observed output or timing for a behavioral one), tradeoffs, your recommendation, and the scratch path. Say plainly that the prototype is throwaway.

## Controls

The one playbook where the Laziness Protocol's "smallest change" and the verification bar invert. Speed over polish, code quality does not matter, no planning. The rigor is in picking the right design cheaply. Propose variations the user didn't ask for, throw an approach away and try another.

## Constraints

**You own the design decision, not the code. The prototype is a throwaway instrument. The real build follows Feature.**

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 1 scopes the decision before anything is built.
- When step 2 applies, the user picks directions before step 3 builds.
- Step 5 observes the variants that steps 3 and 4 build.
