# ALPS Local Runtime UI reference mock

This working mock is an informative reference for the ALPS Local Runtime v0 user experience. It is not a normative part of ALPS and does not define API or domain semantics.

The mock demonstrates the minimum intended interaction surface:

- **Atlas** — an interface-centred bipartite Process Model graph;
- **Runs** — a three-lane projection of Process Instances;
- **Library** — discovery and focused inspection of Skills, Plugins, and Process Models;
- **Skill viewer** — package tree, discovery metadata, rendered `SKILL.md`, and one contextual action;
- **Analysis** — one operational lens at a time;
- **Decision** — a concrete Human Oversight action with verified and unknown conditions.

Open [`index.html`](index.html) directly in a browser. The mock is self-contained and uses no external CDN or framework runtime. It references the repository-authoritative [`assets/icon.svg`](../../../assets/icon.svg) rather than duplicating the icon.

The implementation specification is available in [English](../../local-runtime-v0.md) and [Japanese](../../ja/local-runtime-v0.md).
