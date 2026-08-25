# ALPS Repository Checker Profile v1

Status: Ratified and implemented repository profile.  Profile identifier:
`alps-repository-checker/v1`.

This document defines the machine-checkable profile for this repository.  It
does not define ALPS, Markdown, YAML, CommonMark, or GFM conformance.

## 1. Purpose and scope

The checker validates a deliberately small representation of an ALPS repository
asset.  It answers questions such as:

- Is the asset written in the repository's canonical frontmatter and Markdown
  profile?
- Does its declared representation kind have the required semantic sections?
- Do canonical Skill references resolve within the configured package roots?
- Do an English asset and its Japanese counterpart describe the same semantic
  shape and stable identities?

The profile covers `SKILL.md` representations in this repository, their canonical
Skill references, and the English/Japanese locale pairing convention.  It is a
repository-specific interchange profile, not a general-purpose document parser.
Existing or future assets MAY be migrated to this storage profile; v1 does not
grandfather unshipped model/view variants merely because an older parser accepted
them.

The following words are normative: **MUST** and **MUST NOT** state requirements;
**SHOULD** and **SHOULD NOT** state recommendations; **MAY** states permission.

### Non-goals

The checker MUST NOT claim that a document is ALPS-conformant, that a Process can
achieve its Outcomes, or that a Process was executed.  It MUST NOT become a
general YAML or CommonMark/GFM implementation.  Rendering, link checking,
translation quality, arbitrary Markdown extensions, execution evidence, and
external-service lookups are out of scope.

## 2. Host syntax versus the repository profile

External Host or distribution tooling MAY validate generic YAML or Markdown if it
wants to.  That tooling owns generic-language validity, and the checker MUST NOT
depend on it or reproduce it.  The checker only reads bounded UTF-8 input and
applies the repository profile below.

The checker has one bounded profile extractor.  It recognizes only the delimiters,
headings, lists, tables, containers, and reference spans needed by this profile,
creates one semantic IR, and passes that IR to validators.  A readable construct
outside the profile MUST be reported as `unsupported-profile-syntax`; it MUST NOT
be reported as “invalid YAML”, “invalid Markdown”, or “invalid ALPS”.

## 3. Representation kinds

`metadata.alps.kind` is an optional direct frontmatter field.  When absent, the
kind is `process`.

| Literal value | Representation | Required semantic center |
| --- | --- | --- |
| `process` | Process (default) | Name, Purpose, Outcomes, Activities and Tasks |
| `process-model` | Process Model | Purpose, declared Processes, Relationships |
| `process-reference-model` | Process Reference Model | Purpose, Process entries with Name/Purpose/Outcomes, Relationships |
| `process-view` | Process View | Purpose, Outcomes, Source Processes, Included Activities and Tasks, Application |

No other kind is supported in v1.  A kind value is a literal profile value, not a
request to infer a kind from headings or references.

## 4. Canonical frontmatter

Frontmatter MUST begin on byte/line 1 with `---` and close with a line containing
exactly `---`.  It MUST contain exactly the required direct fields `name` and
`description`, followed by optional `metadata.alps.kind`, in this order and
indentation:

```yaml
---
name: <lowercase-hyphen-name>
description: <one-line-description>
metadata:
  alps.kind: <supported-kind>
---
```

`metadata` MAY be omitted.  If `metadata` is present, it MUST contain exactly
one direct child, the literal key `alps.kind`; an empty `metadata` mapping is
unsupported.  The top-level keys MUST
appear in the order `name`, `description`, then optional `metadata`; the child
indent MUST be exactly two ASCII spaces.  Tabs are never indentation.  A file
with no `metadata.alps.kind` has kind `process`.

For inspected fields (`name`, `description`, and `metadata.alps.kind`):

- The key spelling MUST be unquoted and exact.  The value MUST be one direct,
  single-line plain scalar after the single `: ` separator.
- `name` MUST match `[a-z0-9]+(?:-[a-z0-9]+)*` and MUST be at most 63 characters.
- `description` MUST be non-empty.  For a Process it MUST end in
  `ALPS-conformant.` in English or `ALPS準拠。` in Japanese.  Other kinds need
  only a non-empty description.  This suffix is a repository discovery marker;
  checking its literal presence does not substantiate the Conformance claim.
- `metadata.alps.kind` MUST be one of the four literals in section 3.
- Duplicate keys, empty values, inline comments in an inspected value, and
  continuation lines for an inspected value are unsupported profile syntax.
- Aliases (`*x`), anchors (`&x`), merge keys (`<<`), tags (`!tag`), quoted
  scalars, flow mappings/sequences (`{}` and `[]`), block scalars (`|` and `>`),
  and YAML sequences are not profile forms for inspected fields.  They MUST be
  diagnosed as unsupported profile syntax even if a generic YAML parser accepts
  them.

Unknown top-level keys and unknown children under `metadata` are errors of class
`unsupported-profile-syntax`.  v1 does not preserve an “opaque frontmatter”
namespace: a field is either one of the three inspected fields or unsupported.
This rule bounds the profile extractor and makes typos visible.

These rules describe the profile's accepted representation.  They do not assert
that any rejected text is invalid YAML.

## 5. Canonical Markdown grammar

### 5.1 Bytes and line structure

The input MUST decode as UTF-8 without a BOM or NUL.  LF is canonical.  CRLF MAY
be normalized to LF before parsing; a bare CR is unsupported.  The checker MUST
retain source line numbers and MUST reject a file that exceeds the resource limits
in section 10.

There MUST be exactly one unindented ATX H1, written as `# ` followed by a
non-empty title.  It MUST be at column zero, MUST NOT use a closing `#` sequence,
and MUST NOT be Setext.  The separator after `#` is one literal ASCII space; a
tab is unsupported profile syntax.  The title is display text and need not equal the
lowercase frontmatter `name` or the translated title in a locale file.

Profile section headings MUST be unindented ATX H2 lines with exact, locale-specific
text.  They MUST NOT have closing markers, Setext underlines, leading spaces, or
heading aliases.  A recognized H2 may occur at most once and sections MUST occur
in the order specified by kind below.  An unrecognized H2 is unsupported profile
syntax, not an arbitrary Markdown section.

English and Japanese semantic headings are paired as follows:

| English | Japanese |
| --- | --- |
| Purpose | 目的 |
| Outcomes | 成果 |
| Activities & Tasks | 活動とタスク |
| Inputs | 入力 |
| Outputs | 出力 |
| Entry Criteria | 開始基準 |
| Exit Criteria | 完了基準 |
| Controls | 統制事項 |
| Constraints | 制約 |
| Enablers | 実行支援要素 |
| Conformance | 適合 |
| Interfaces & Traceability | インターフェースと追跡可能性 |
| Shared Normative References | 共通規範参照 |
| Bundled Resources | 同梱資源 |
| Common Approach | 一般的な進め方 |
| Processes | プロセス |
| Relationships | 関係 |
| Source Processes | 出典プロセス |
| Included Activities and Tasks | 含まれる活動およびタスク |
| Application | 適用 |
| Verification | 検証 |

After translating the heading names with the table above, the following order is
normative.  Optional headings MAY be omitted, but a present heading MUST appear
in this order and MUST NOT be duplicated:

- Process: `Purpose`, `Outcomes`, `Activities & Tasks`, then optional `Inputs`,
  `Outputs`, `Entry Criteria`, `Exit Criteria`, `Controls`, `Constraints`,
  `Enablers`, `Conformance`, `Interfaces & Traceability`, `Shared Normative
  References`, `Bundled Resources`, and `Common Approach`.
- Process Model: `Purpose`, `Processes`, `Relationships`, then optional
  `Application`, `Verification`, `Conformance`, and `Bundled Resources`.
- Process Reference Model: `Purpose`, `Processes`, `Relationships`, then
  optional `Application`, `Verification`, `Conformance`, and `Bundled Resources`.
- Process View: `Purpose`, `Outcomes`, `Source Processes`, `Included Activities
  and Tasks`, `Application`, then optional `Conformance` and `Bundled Resources`.

Every profile H3 or H4 role heading MUST be an unindented ATX heading without a
closing marker or Setext underline.  Its text is an exact localized heading when
the role names one; otherwise the text is the bounded display label of the
entry.  No heading role is inferred from a near-match.

Within every required `Purpose` block, H3-H6 are unsupported profile syntax.
The extractor MUST ignore those headings when collecting Purpose prose and MUST
report them even when other prose is present.  Only non-heading visible prose
can make a required Purpose non-empty.  The required Process View `Application`
block follows the same rule: H3-H6 are unsupported, cannot count as visible
Application content, and cannot make an otherwise empty Application valid.

H3 and H4 are structural only where a kind assigns them a role:

- In a Process, an unindented H3 whose text is the Activity label starts one
  Activity block, which ends at the next H3 or section H2.  The block MAY begin
  with opaque introductory prose.  It MUST contain exactly one unindented
  contiguous ordered Task list before the next H3.  H4-H6, a second list, or a
  child heading inside the machine-bearing Activities section are unsupported
  profile syntax and never create records.
- In a Process Model, the `Processes` section is one table; H3-H6 there are
  unsupported profile syntax.
- In a Process Reference Model, each unindented H3 under `Processes` starts one
  Process entry.  Its next semantic headings MUST be exact H4 `Purpose`/`目的`
  followed by exact H4 `Outcomes`/`成果`; no other H4-H6 is permitted in the
  entry block.
- In a Process View, `Source Processes` and `Included Activities and Tasks` are
  tables; H3-H6 in those machine-bearing sections are unsupported profile syntax.
- H3-H6 in optional opaque sections never create profile records and are not
  interpreted by this checker.  They cannot satisfy or replace a required H2,
  Activity, Process entry, list, or table.

### 5.2 Lists and continuations

In a machine-bearing section, profile lists use only an unindented `- ` bullet
for Outcomes or an unindented contiguous decimal list (`1. `, `2. `, ...) for
Process Tasks.  A Task list MUST start at `1.` and increment by one for each
item.  `*`, `+`, `1)`, arrow relationship items, Process Model Process lists,
View non-table items, nested lists, and indented list containers are unsupported.
A continuation line MUST begin with exactly three spaces and non-empty text; it
is joined to the preceding item with one space and cannot create another record.
A blank line ends the contiguous list.  An indented code block is unsupported
profile syntax, not an accepted opaque construct.

List-like text in an optional opaque section is retained as opaque section text;
it is not tokenized as a profile list or generically validated.  It cannot create
an Outcome, Task, Process entry, or View inclusion.

An Outcomes section MAY begin with opaque introductory prose.  It MUST contain
exactly one unindented hyphen list; the prose cannot create an Outcome.  No
Outcome table, paragraph, heading, or mixed representation creates an Outcome
record, and a missing list fails the required section.  Each Activity block MUST
contain exactly one unindented ordered Task list, after any opaque introduction
and before the next H3.  H4-H6, a second list, and any list outside that position
are unsupported.

### 5.3 Canonical tables

Only a table in a designated machine-bearing section is a profile table.  Such a
table MUST have outer pipes on every line, an exact header row, an exact separator
row, and data rows of exactly the header width.  The separator cells MUST be
`---`; alignment markers, omitted outer pipes, blank separator lines, short rows,
extra cells, and arbitrary row padding are unsupported.  A pipe inside a cell is
unsupported in v1.  Each machine-bearing table below occurs exactly once; a
second table, a mixed list/table representation, or a malformed neighboring line
in that section is unsupported profile syntax.

The only machine-bearing table schemas are:

| Section | English header | Japanese header | Width and cell rule |
| --- | --- | --- | ---: |
| Process Model `Processes` | `Process \| Skill` | `プロセス \| スキル` | 2; Skill is empty or one single-backtick reference |
| Process Model/Reference Model `Relationships` | `Provider Process \| Information \| Recipient Process \| Relationship` | `提供側プロセス \| 情報 \| 受領側プロセス \| 関係` | 4 |
| Process View `Source Processes` | `Source Process \| Reference` | `出典プロセス \| 参照` | 2; Reference is exactly one single-backtick reference |
| Process View `Included Activities and Tasks` | `Source Process \| Source element` | `出典プロセス \| 出典要素` | 2; Source element starts with the exact kind prefix |

No table is permitted for Outcomes.  Process Model Process entries use only the
fixed `Process | Skill` table; no list or heading form is recognized.  Header
aliasing, header reordering, two-column relationship inference, multiple table
blocks, and general GFM table behavior are not supported.

These schemas are not a general table parser.  Table-like text in an optional
opaque section such as `Interfaces & Traceability` is retained as opaque section
text; it is not tokenized as a table, generically validated, or used to create
records.  The same text does not satisfy a required machine-bearing table.

In a relationship table, each Provider Process and Recipient Process cell MUST
be exactly one declared non-empty display name.  Skill references are not a
second relationship-endpoint form; a reference in one of these endpoint cells
is unsupported.  The Information and Relationship cells are opaque non-empty
text; they do not create additional records.  In a View Source
Processes row, the Source Process cell is a non-empty display name and the
Reference cell is exactly one reference.  In an Included Activities and Tasks
row, the Source Process cell is the concatenation of a declared non-empty display
name, one ASCII space, `(`, one of the exact single-backtick reference forms from
section 6, and `)` with no trailing text.  The reference MUST equal that source's
declared Reference cell.  The Source element cell MUST begin at column zero with
the exact literal prefix `Activity: ` or `Task: ` plus a non-empty label
(localized `活動: ` or `タスク: `).

### 5.4 Fences, blockquotes, comments, and prose

An unindented fenced block is opened by at least three consecutive backticks or
tilde characters at column zero.  Its optional info text is opaque; a closing
run of the same character with at least the opening length and only trailing
spaces ends it.  The block's headings, lists, tables, and references MUST NOT
enter the IR.  An unclosed fence, a fence nested in a list/container, or an
indented fence is unsupported profile syntax.  Blockquotes are likewise opaque
and do not produce profile records; nested container variants are unsupported.

Any indented code block, including a four-space line that resembles a list,
heading, table, or reference, is unsupported profile syntax.  It is not an
accepted opaque form and MUST NOT be silently ignored as valid profile input.

An HTML comment from `<!--` through `-->` is opaque and contributes no records or
references.  An unclosed comment is unsupported.  Ordinary paragraphs and other
prose are retained only as opaque section text: they never become an Activity,
Task, Outcome, Process entry, table row, or View inclusion.  Prose cannot satisfy
a required machine-bearing section.

Raw HTML tags and blocks are not opaque profile containers.  They are
`unsupported-profile-syntax`, and heading-, list-, table-, or reference-like text
between their tags MUST NOT enter the IR.  In particular, a `<pre>` block cannot
supply a Name or required section by containing lines that resemble ATX headings.
This is a bounded profile rule, not general HTML-block parsing or validation.

## 6. Canonical Skill references

The only operative form is one exact single-backtick span containing one bounded
token:

```text
`skill:#<skill-name>`
`skill:<package-id>#<skill-name>`
```

`<skill-name>` is one lowercase-hyphen identifier.  `<package-id>` is one or more
lowercase-hyphen segments separated by `/`, matching
`[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*`.  Empty segments, `.`, `..`,
backslashes, and other separators are rejected.  Thus `mashimashica/alps` is
valid, while `mashimashica//alps`, `mashimashica/./alps`, and
`mashimashica/../alps` are not.

Bare `skill:` text is always a non-operative lookalike, including in ordinary
prose.  A dedicated line and a designated table cell still use the exact form,
for example:

```markdown
Skill: `skill:mashimashica/alps#define-alps`
```

In an identity-bearing table row or Reference Model entry, the designated field
MUST contain zero or one exact single-backtick reference as its schema specifies;
multiple references are a profile/semantic error.

The following are non-operative lookalikes: bare tokens, tokens in a fence,
blockquote, HTML comment, or indented code, Markdown link destinations,
double-backtick or other non-canonical code spans, malformed/case-variant tokens,
and package identifiers with empty, dot, or dot-dot segments.  A lookalike MUST
NOT be resolved or create an IR identity.  A malformed reference in a designated
reference field is an `unsupported-profile-syntax` error.

Resolution MUST use the configured package identity and a real path contained by
that package root.  A `..` escape, or a symlink whose resolved target escapes the
configured package root, is an error.  Symlinks whose resolved target remains
inside that package root are permitted.  The target MUST be a Process
representation where the surrounding rule requires a Process.  No network or
registry lookup is permitted.

After filesystem resolution succeeds, the canonical identity is exactly
`ResolvedReference.identity`: the resolved package identity plus `#` plus the
resolved skill name.  Therefore, when `skill:#x` resolves within package `pkg`,
it and `skill:pkg#x` are the same canonical identity and MUST be treated as one
identity for uniqueness, binding, and semantic comparison.  The lexical token,
source span, and original qualification MUST remain unchanged in the IR; they
are presentation/provenance data, not semantic identity.  A reference that does
not resolve has no canonical identity and MUST retain its resolution error; the
checker MUST NOT make an unresolved short or qualified token valid by falling
back to lexical comparison.

The canonical reference is the locale-independent identity.  Its authoritative
path is the target package's `skills/<skill-name>/SKILL.md`.  When validating a
Japanese asset, the checker uses that target's
`references/locales/ja/SKILL.md` for localized display and semantic-center
comparison when the counterpart exists.  Absence of that counterpart is an
error only when locale completeness is required.  Resolution never changes the
canonical identity or infers one from translated text.

## 7. Semantic requirements

The parser produces one semantic IR before any validator runs.  Text is normalized
only for the specified comparison operations: line continuations become one
space, list/table cell edge whitespace is removed, and locale-specific display
text remains text rather than being guessed as an English translation.

### Process

The asset MUST contain non-empty `Purpose`, at least one `Outcome`, at least one
Activity, and at least one Task under every Activity.  Outcomes MUST come only
from the one unindented hyphen list; introductory prose is opaque, and an Outcome
table or paragraph is not an alternative.  Each Activity block MAY begin with
opaque prose but MUST contain exactly one unindented ordered Task list before the
next H3; H4-H6, a second list, or a child heading in that machine-bearing section
is an error.  Each Task MUST contain at least one recognizable normative marker
(`must`, `must not`, `should`, `should not`, `may`, or `typically`, with the
defined Japanese equivalents).  Markers are recognized as non-overlapping
tokens.  If two markers begin at the same position, the longer negative form is
preferred (`must not` before `must`, and `should not` before `should`).  The
governing class is the last recognized marker in the Task text, so a conditional
need and a later governing recommendation are allowed.

The required `Purpose` is formed only from non-heading visible prose.  H3-H6 in
the block are `unsupported-profile-syntax` errors, whether the block contains
only such headings or contains headings alongside prose.

| Class | English marker | Japanese marker family |
| --- | --- | --- |
| `must-not` | `must not` | `てはならない`, `ではならない`, `禁止される` |
| `must` | `must` | `必要がある`, `なければならない` |
| `should-not` | `should not` | `のが望ましくない`, `ことが望ましくない`, `避けるのが望ましい` |
| `should` | `should` | `のが望ましい`, `ことが望ましい` |
| `may` | `may` | `てよい`, `でもよい`, `てもよい`, `でよい` |
| `typically` | `typically` | `通常`, `典型的` |

`Inputs`, `Outputs`, criteria, controls, constraints, enablers, conformance,
traceability, resource, and approach sections are optional opaque/profile
sections in the canonical order; they do not create additional Process records.

The only v1 natural-language heuristics beyond normative markers are bounded as
follows.  An Outcome matching English
`\b(?:is|are|was|were)\s+(?:only\s+)?(?:recorded|documented)\b` (case-insensitive)
or Japanese `(?:が|は)(?:記録|文書化)されている` produces a `quality-review`
warning; it does not fail the asset.  An `Inputs` section matching English
`\bapplicable Controls?\b` (case-insensitive) or Japanese
`適用(?:される)?(?:統制事項|Control)` is a `semantic` error because a Control has
been classified as an Input.  The checker MUST NOT infer other natural-language
classifications in v1.

### Process Model

`Purpose`, `Processes`, and `Relationships` are required and non-empty.  The
Purpose heading rule above applies before the Process Model table is extracted.
The `Processes` section MUST contain exactly one `Process | Skill` table.  Every row
MUST have a non-empty Process display name and a unique identity.  Its Skill cell
MUST be empty or contain exactly one single-backtick reference.  A supplied
reference MUST resolve to a Process and the display name MUST agree with its H1
after profile normalization.  A Process list or Process heading is unsupported.

The `Relationships` section MUST contain exactly one four-column relationship
table.  Every row MUST have a declared provider and recipient display name in
the fixed columns; no arrow-list or second table is accepted.  An undeclared
endpoint or endpoint display name that disagrees with the declared Process is an
error.

### Process Reference Model

`Purpose`, `Processes`, and `Relationships` are required.  The top-level Purpose
and each required entry Purpose use only non-heading visible prose; H3-H6 in
either Purpose block are unsupported profile syntax.  Every H3 Process entry
MUST contain, in order, exact H4 `Purpose` and exact H4 `Outcomes`.  Its Outcomes
section MUST use the one unindented hyphen list.  An entry MAY contain one exact
Skill line as its first non-blank line after the H3 and before the first H4,
whose English and Japanese accepted shapes are:

```text
Skill: `skill:#<skill-name>`
Skill: `skill:<package-id>#<skill-name>`
スキル: `skill:#<skill-name>`
スキル: `skill:<package-id>#<skill-name>`
```

If supplied, the reference MUST resolve to a Process and the entry's Name,
normalized Purpose, and ordered Outcome IR MUST equal the target Process.  Other
H4-H6 forms are unsupported.  Relationships MUST use exactly one four-column
relationship table, as in the Process Model.

### Process View

`Purpose`, `Outcomes`, `Source Processes`, `Included Activities and Tasks`, and
`Application` are required and non-empty.  The Purpose and Application heading
rules above apply to these required blocks: H3-H6 are diagnosed and never count
as prose.  At least two distinct Source Processes
MUST be declared by exactly one `Source Process | Reference` table.  Each row's
Reference cell MUST contain exactly one single-backtick Skill reference that
resolves to a Process; its Source Process cell is the display name and MUST agree
with the target.  Source display names and reference identities MUST each be
unique within the declaration table.

The `Included Activities and Tasks` section MUST contain exactly one
`Source Process | Source element` table.  Each row's Source Process cell MUST
identify one declared source with exactly one single-backtick reference, and its
Source element cell MUST start with exact `Activity: <label>` or `Task: <label>`
(localized `活動: <label>` or `タスク: <label>`).  Non-table inclusions, multiple
provenance tables, and mixed forms are unsupported.  An undeclared source,
unresolved reference, missing kind prefix, or duplicate complete
`(source identity, kind, label)` inclusion is an error.  Multiple distinct
included elements MAY use the same declared Source Process.  The View's local
Outcomes and Application are not silently treated as source Process Outcomes or
execution.

## 8. Locale pairing and comparison

The English asset is `.../SKILL.md`; its Japanese counterpart is the sibling
`.../references/locales/ja/SKILL.md`.  A pair is compared only after both
documents have independently passed profile parsing and have produced IRs.  The
checker MUST compare IR fields, never raw Markdown or regular-expression matches
over the two source files.

The pair MUST have the same frontmatter `name` and kind.  If a containing or
configured package identity is available, comparison MUST use that context to
normalize a local `skill:#x` to the same semantic identity as a resolved
same-package `skill:pkg#x`; a resolved reference to a different package remains
a mismatch.  This normalization affects only comparison and never rewrites the
lexical IR token or span.  The following semantic shape is compared in order.
Identities come only from the parsed IR: canonical single-backtick references,
fixed table fields, and the exact entry structures defined above.  A
display-name similarity or a reference-looking string in opaque prose is not an
identity.

- Process: Outcome count and resolved reference sequence, Activity count, Task
  counts by Activity, and normative class for each corresponding Task.
- Process Model: resolved Process identity/order and resolved relationship
  provider/recipient identity/order.  When a Process table row has an empty Skill cell, a
  name-based comparison MAY produce an `unverified-locale-identity` warning;
  it MUST NOT infer an identity from arbitrary prose.
- Process Reference Model: resolved Process identity/order, each resolved
  referenced semantic center, and resolved relationship provider/recipient
  identity/order.
- Process View: resolved Outcome identity/order, resolved Source Process
  identity/order, and Included Activity/Task kind and resolved source
  identity/order.

Localized prose, headings, and display labels are not required to be byte-equal.
Missing or unstable identity produces a warning only when the profile can still
compare counts and kinds; a proven count, kind, or stable-reference mismatch is
an error.  A missing required Japanese counterpart is an error only when the
caller requests locale completeness.

## 9. Diagnostics and exit behavior

Every diagnostic has a class, severity, path, and source line when available.

| Class | Severity | Meaning |
| --- | --- | --- |
| `host-input` | error | Cannot read/decode the bounded input or host cannot supply required boundaries |
| `unsupported-profile-syntax` | error | A readable construct is outside this profile; never call it invalid YAML/Markdown |
| `profile-structure` | error | A canonical field, heading, list, table, or required section is malformed or missing |
| `semantic` | error | Kind rule, reference resolution, identity, or source/provenance rule fails |
| `locale-mismatch` | error | Paired IRs have different required semantic shape or stable identity/order |
| `unverified-locale-identity` | warning | Pair comparison is possible only by a non-stable display/name fallback |
| `quality-review` | warning | Informative review candidate that does not invalidate the profile |
| `internal` | error | Checker invariant or implementation failure |

Exit status MUST be `0` when no errors occur, even if warnings are emitted; `1`
when one or more document/profile/semantic/locale errors occur; and `2` for
checker invocation, configuration, unreadable-input, or internal failures that
prevent a reliable document finding.  Unsupported profile syntax is a document
error and therefore returns `1`.  Internal failures MUST return `2`.  A status of
`0` means only “valid under ALPS Repository Checker Profile v1”; it is not an
ALPS Conformance claim.

## 10. Architecture and resource limits

The implementation SHOULD be stdlib-only and MUST have these boundaries:

1. Read and bound the input.
2. Parse frontmatter and visible Markdown once into one typed IR, retaining source
   spans and container state.  Regex MAY be used only for bounded tokens such as
   names, kinds, references, exact heading lines, list markers, and table
   separators.
3. Resolve references and normalize locale identity in the IR layer.
4. Run kind validators and locale validators over IR.  Validators MUST NOT read
   raw Markdown, call regex over raw source, or re-extract tables independently.

A reasonable v1 implementation split is `input`, `frontmatter_profile`,
`markdown_profile`, `reference_profile`, `ir`, `validators`, `locale_compare`,
and `cli`.  The extractor MUST NOT import PyYAML, a Markdown parser, a network
client, or a package registry.

The v1 limits are: at most 1 MiB per asset, 20,000 normalized lines, 8 KiB per
normalized line, 256 KiB of frontmatter, and 512 profile records per section.
The scanner rejects nested opaque containers and has at most one simultaneously
active opaque-container state (`MAX_ACTIVE_CONTAINER_STATES = 1`); a closed
container releases that state.  This is a constant-space v1 rule, not a 32-state
heading stack.  The implementation MUST enforce these bounds before allocating
an unbounded collection.  Exceeding a limit is a `profile-structure` error.
At most 512 distinct operative lexical reference tokens per asset are retained
in the document-level aggregate used for resolution and allocation.  Repeated
references inside an Outcome, Task, or Application record remain ordered in
that record's IR for locale comparison; short and qualified spellings remain
distinct lexical tokens until validator resolution normalizes them.  Limits are
part of the profile contract and MUST be tested.  The exact 256 KiB frontmatter
guard is tested independently with deliberately rejected filler:
canonical v1's five-line mapping reaches stricter field and line grammar before
that upper byte guard can be a valid asset.

## 11. Accepted and rejected examples

Accepted frontmatter:

```yaml
---
name: example-process
description: Defines an example Process. ALPS-conformant.
---
```

Accepted kind declaration:

```yaml
---
name: example-view
description: Organizes source Processes.
metadata:
  alps.kind: process-view
---
```

Accepted canonical relationship table:

```markdown
| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS | Evidence | Manage ALPS | Supports adoption. |
```

Accepted canonical Process task structure:

```markdown
## Activities & Tasks

### Review

1. The agent must inspect the input.
2. The agent should record the result.
```

Accepted canonical Process Model declarations:

```markdown
| Process | Skill |
| --- | --- |
| Define ALPS | `skill:mashimashica/alps#define-alps` |
| Manage ALPS | |
```

Accepted canonical Process Reference Model entry:

```markdown
### Define ALPS

Skill: `skill:mashimashica/alps#define-alps`

#### Purpose

Define the profile.

#### Outcomes

- The profile is defined.
```

Accepted canonical Process View tables:

```markdown
## Source Processes

| Source Process | Reference |
| --- | --- |
| Define ALPS | `skill:mashimashica/alps#define-alps` |
| Manage ALPS | `skill:mashimashica/alps#manage-alps` |

## Included Activities and Tasks

| Source Process | Source element |
| --- | --- |
| Define ALPS (`skill:mashimashica/alps#define-alps`) | Activity: Review |
| Manage ALPS (`skill:mashimashica/alps#manage-alps`) | Task: Record result |
```

Rejected as `unsupported-profile-syntax`, not invalid YAML/Markdown:

```yaml
metadata: &m
  alps.kind: process-view
```

```markdown
Process | Skill
--- | ---
Define ALPS | `skill:#define-alps`
```

```markdown
### Review

#### Tasks

1. The agent must do work.
```

```markdown
- Define ALPS -> Manage ALPS
```

```markdown
Skill: skill:mashimashica/alps#define-alps
```

Setext headings, `## Purpose ##`, a heading indented by one space, a table row
with a missing or extra cell, a second or mixed machine-bearing table, an
aliased/merged frontmatter mapping, a nested list, an indented code block, and a
Skill token inside a fence are likewise outside v1.  The checker reports the
boundary and does not attempt to reinterpret the construct as a different
profile form.

## 12. Change control and versioning

The profile version is an explicit checker contract, currently `v1`.  A change
that alters accepted syntax, rejected syntax, IR meaning, identity normalization,
diagnostic class/severity, or exit behavior MUST use a new profile version and a
new golden fixture set.  A narrower v1 implementation MAY clarify wording without
changing behavior; it MUST record such clarifications in the change review.

Adding a new optional syntax is still a profile change because it changes the
machine-checkable language; it is not silently backported to v1.  The checker MUST
report its profile version, and tests MUST pin that value.  This v1 profile is
ratified together with the canonical assets, typed IR contract, diagnostics, and
profile-focused replacement suite.  Future behavior changes MUST follow the
versioning rule above and be reviewed as a new profile revision.

## 13. Explicitly out of scope

- General YAML validity (which remains the Host/distribution tooling's concern),
  YAML 1.1/1.2 typing, aliases, merges, tags, arbitrary
  sequences, flow collections, block scalars, or YAML schema resolution.
- General Markdown/CommonMark/GFM validity, Setext headings, arbitrary table
  layouts, nested containers, renderer behavior, HTML, links, emphasis, and
  arbitrary code-span rules.
- Inferring semantic headings, table columns, list roles, kinds, or locale
  mappings from near-matches or natural-language labels.
- ALPS Conformance, Process execution, Outcome achievability, evidence quality,
  translation naturalness, or source meaning beyond the bounded semantic checks.
- Network resolution, remote packages, registries, GitHub, or external services.
- A compatibility promise for the parser behavior covered by the discarded
  general YAML/Markdown compatibility tests.
