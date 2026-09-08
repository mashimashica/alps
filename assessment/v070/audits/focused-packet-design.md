# Focused evidence packet preparation

`prepare_focused_grading.py` implements only the six packets fixed in
`focused-grading-allocation.json`. It performs no generation, application,
grading, source repair, native-state capture, or remote write. It is intended
for independent infrastructure review before use.

Usage, after all four creators and eight applications in a packet are explicitly
complete:

```sh
python -B prepare_focused_grading.py FP01 --check-only
python -B prepare_focused_grading.py FP01
```

Replace `FP01` with exactly one of `FP01`–`FP06`. There is no arbitrary creator
selection or automatic retry. `--check-only` performs the same read-only
preflight and creates no output. Preparation writes `blind-focused/FPxx/` and
the external `blind-mappings/focused-FPxx.json` and
`blind-mappings/focused-FPxx-provenance.json`. Any existing or partial output
causes refusal; late failure retains all partial files for reconciliation.

The script pins the plan, allocation, business-bank manifests, oracle manifest,
and grading guidance. A redundant six-packet table checks every R17/R63/R28/R44
mapping and both reviewer filenames. It also verifies the existing fixed C
schedules and exact focused creator/consumer schedules, their mutable assignment
fields, and explicit completion for every selected creator and application.
It checks twelve selected completion rows again after copying.

Original creator inputs/prompts, package sources, frozen Skill resources, public
creator notes, recorded physical-format evidence, consumer assignments, common
aid, raw variants, and consumer prompts remain separately identified. Each
consumer's recorded initial hashes and modes must equal its frozen Skill and
raw variant, including only the prescribed path substitutions and unchanged
public interface. Final input and Skill changes are preserved and described,
including deletions, additions and changed modes; the packager assigns no grade
to those changes. All application work and additional application files are
included. New creator/application public handoffs remain separate files.

The eight reused C creators come only from the verified selected candidate
trees in S03-P01/P02 and S06-P01/P03. The script pins their original external
mapping and provenance hashes, checks their exact candidate file set and modes,
and rechecks every original source role or reviewed recovery derivation against
the prior candidate. It then copies every candidate file unchanged under the
new preallocated label. There is no fallback that rebuilds missing originals.
Runtime caches are the sole existing, explicit exclusion; all excluded hashes
and observed modes remain in external provenance and original cache bytes stay
at source.

For recovered S06 applications, the existing reviewed recovery planner verifies
the original assignment, surviving observations, source relays, and separately
labeled logical-state supplements. The previously packaged availability text
and recovery provenance are copied unchanged. Missing final metadata and
workflow SQLite evidence remain missing. C-U094/095/096 retain the original
initial-state chain, restored-state binding and final native observations.

For C071/072 creator evidence, the script uses
`recovered_control_grading.plan_creator` and its closed candidate-file plan. It
copies the reviewed canonical package, public note, retained authored-text
relay and physical-format observation. The candidate receives the exact
substantive origin and historical-limit statements; the full coordinator
provenance remains outside the grader packet. Recovery-time modes and freezes
are never described as lost original observations.

S06 F evidence is read from `consumer-setup/F-Uxxx.json` and
`state-snapshots/F-Uxxx/{initial,final}.{json,sql}`. The assignment must bind the
exact initial files, raw fixture, public interface, state path and original
init/describe observations. Both metadata files must bind the matching consumer,
snapshot label, allocated path and SQL digest. F applications cannot borrow a
C recovery binding. The packager never opens a live original database. Native
SQL describes committed logical state, not original SQLite bytes or call history.

Before and after copying, source files and whole observed source inventories
must retain their SHA-256 values and modes. Exclusive writes preserve each
source mode, and the complete destination file set/hashes/modes must equal the
preflight plan. Symlinks, noncanonical paths, unsupported entries, unknown
resources in closed original/recovery inventories, duplicate destinations and
partial outputs are refused.
The new mapping, completion rows, source-to-copy identities and provenance stay
outside the packet. Source metadata and prior grades are not copied; an explicit
arm/model/repetition-label scan fails for review rather than redacting substantive
evidence. Original paths and stylistic hints remain, so blinding is procedural
and incomplete by design.

The grader receives raw business oracles, fixed grading guidance, the original
business description, both raw case variants and all four candidate/application
evidence sets. The boundaries explicitly permit the existing optional
`frozen/skill-creator/SKILL.md` and needed resources. Its complete identity is
verified and recorded externally; it is not duplicated into each packet.
Focused judgment boundaries retain all
assigned slots, separate task adequacy from Outcome and component correctness,
and distinguish evidenced corrections from ordinary interpretation or missing
observations. These instructions contain no prior judgments or release gates.

Implementation verification in this change is limited to static syntax and
interface inspection. Actual packet preparation and trial execution are not
part of this implementation task.
