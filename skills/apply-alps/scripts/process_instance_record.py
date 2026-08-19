#!/usr/bin/env python3
"""Create and check the lightweight Markdown Process Instance binding."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


FORMAT = "process-instance-record/1"
HEADING_RE = re.compile(r"^ {0,3}(#{2,6})\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^ {0,3}-[ \t]+`([^`]+)`:\s*(.*?)\s*$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
RAW_HTML_RE = re.compile(
    r"(?:</?[A-Za-z][A-Za-z0-9-]*(?:[ \t/>]|$)|<\?|<![A-Za-z]|<!\[CDATA\[)",
    re.IGNORECASE,
)
REPEATABLE_FIELDS = {"evidence", "limitations"}
LINE_BREAKS = frozenset("\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029")
CORE_KINDS = {
    "application",
    "activity",
    "purpose",
    "outcome",
    "task",
    "success_criterion",
    "input",
    "output",
    "entry_criterion",
    "exit_criterion",
    "control",
    "constraint",
    "enabler",
    "exchange",
    "decision",
    "handoff",
    "tailoring",
    "conformance",
}
EXTENSION_KIND_RE = re.compile(r"^x_[a-z0-9]+(?:_[a-z0-9]+)*$")
LOCALES = {
    "en": {
        "application_basis": "Application basis",
        "purpose": "Purpose",
        "outcome": "Intended Outcome",
        "task": "Task",
        "criterion": "Success criterion",
        "created": "created",
        "error": "ERROR",
        "valid": "valid {format} binding at {at}: {path}",
    },
    "ja": {
        "application_basis": "適用の基礎",
        "purpose": "Purpose",
        "outcome": "意図するOutcome",
        "task": "Task",
        "criterion": "成功基準",
        "created": "作成しました",
        "error": "エラー",
        "valid": "{at}時点で{format} Bindingに適合: {path}",
    },
}


@dataclass
class Block:
    heading: str
    line: int
    fields: dict[str, list[str]] = field(default_factory=dict)

    def values(self, key: str) -> list[str]:
        return [value.strip() for value in self.fields.get(key, []) if value.strip()]

    def value(self, key: str) -> str:
        values = self.values(key)
        return values[0] if values else ""


def one_line(value: str, option: str) -> str:
    if any(character in LINE_BREAKS for character in value):
        raise ValueError(f"{option} must be a single line")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{option} must be valid UTF-8") from exc
    value = value.strip()
    if not value:
        raise ValueError(f"{option} must not be empty")
    return value


def field_line(key: str, value: str = "") -> str:
    return f"- `{key}`: {value}".rstrip()


def statement_block(heading: str, kind: str, statement: str) -> list[str]:
    return [
        f"## {heading}",
        field_line("kind", kind),
        field_line("source_statement", statement),
        field_line("instance_statement"),
        field_line("criterion"),
        field_line("result"),
        field_line("assessment"),
        field_line("evidence"),
        field_line("limitations"),
    ]


def criterion_block(criterion: str, heading: str) -> list[str]:
    return [
        f"## {heading}",
        field_line("kind", "success_criterion"),
        field_line("criterion", criterion),
        field_line("result"),
        field_line("assessment"),
        field_line("evidence"),
        field_line("limitations"),
    ]


def render_record(args: argparse.Namespace) -> str:
    labels = LOCALES[args.locale]
    values = {
        "title": one_line(args.title, "--title"),
        "source": one_line(args.source, "--source"),
        "context": one_line(args.context, "--context"),
        "scope": one_line(args.scope, "--scope"),
    }
    for name in ("purpose", "outcome", "task", "criterion"):
        setattr(args, name, [one_line(item, f"--{name}") for item in getattr(args, name)])

    if not args.outcome and not args.criterion:
        raise ValueError("new requires at least one --outcome or --criterion")

    lines = [
        f"# {values['title']}",
        "",
        f"## {labels['application_basis']}",
        field_line("kind", "application"),
        field_line("record_format", FORMAT),
        field_line("source", values["source"]),
        field_line("context", values["context"]),
        field_line("scope", values["scope"]),
    ]
    for statement in args.purpose:
        lines.extend(["", *statement_block(labels["purpose"], "purpose", statement)])
    for statement in args.outcome:
        lines.extend(["", *statement_block(labels["outcome"], "outcome", statement)])
    for statement in args.task:
        lines.extend(["", *statement_block(labels["task"], "task", statement)])
    for criterion in args.criterion:
        lines.extend(["", *criterion_block(criterion, labels["criterion"])])
    return "\n".join(lines) + "\n"


def parse_record(path: Path) -> tuple[list[Block], list[str]]:
    text = path.read_text(encoding="utf-8")
    blocks: list[Block] = []
    errors: list[str] = []
    current: Block | None = None
    fence_character = ""
    fence_length = 0
    in_comment = False
    html_comment_seen = False
    raw_html_seen = False
    for number, line in enumerate(text.splitlines(), start=1):
        if fence_character:
            fence = FENCE_CLOSE_RE.match(line)
            if fence:
                marker = fence.group(1)
                if marker[0] == fence_character and len(marker) >= fence_length:
                    fence_character = ""
                    fence_length = 0
            continue

        visible = ""
        remainder = line
        if "<!--" in remainder or "-->" in remainder:
            html_comment_seen = True
        while remainder:
            if in_comment:
                end = remainder.find("-->")
                if end < 0:
                    remainder = ""
                    break
                remainder = remainder[end + 3 :]
                in_comment = False
                continue
            start = remainder.find("<!--")
            if start < 0:
                visible += remainder
                break
            visible += remainder[:start]
            remainder = remainder[start + 4 :]
            in_comment = True
        line = visible

        if RAW_HTML_RE.search(line):
            raw_html_seen = True
            continue

        fence = FENCE_OPEN_RE.match(line)
        if fence:
            marker = fence.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        heading = HEADING_RE.match(line)
        if heading:
            current = Block(heading=heading.group(2), line=number)
            blocks.append(current)
            continue
        item = FIELD_RE.match(line)
        if item and current is not None:
            current.fields.setdefault(item.group(1), []).append(item.group(2))
    if fence_character:
        errors.append("unclosed fenced code block")
    if html_comment_seen:
        errors.append("HTML comments are not allowed in the visible binding")
    if in_comment:
        errors.append("unclosed HTML comment")
    if raw_html_seen:
        errors.append("raw HTML blocks are not allowed in the visible binding")
    return blocks, errors


def require(block: Block, keys: tuple[str, ...], errors: list[str]) -> None:
    for key in keys:
        if not block.value(key):
            errors.append(f"line {block.line} ({block.heading}): `{key}` is required")


def check_record(path: Path, at: str) -> list[str]:
    blocks, errors = parse_record(path)
    for block in blocks:
        if "kind" in block.fields and not block.value("kind"):
            errors.append(
                f"line {block.line} ({block.heading}): `kind` must not be empty"
            )
    bound = [block for block in blocks if block.value("kind")]

    for block in bound:
        kind = block.value("kind")
        if kind not in CORE_KINDS and not EXTENSION_KIND_RE.fullmatch(kind):
            errors.append(
                f"line {block.line} ({block.heading}): unknown `kind` {kind!r}; "
                "local extensions must use an `x_` prefix"
            )
        for key, values in block.fields.items():
            if key not in REPEATABLE_FIELDS and len(values) > 1:
                errors.append(
                    f"line {block.line} ({block.heading}): `{key}` must occur once"
                )

    applications = [block for block in bound if block.value("kind") == "application"]
    if len(applications) != 1:
        errors.append("exactly one block with `kind`: application is required")
    else:
        application = applications[0]
        require(application, ("record_format", "source", "context", "scope"), errors)
        record_format = application.value("record_format")
        if record_format and record_format != FORMAT:
            errors.append(
                f"line {application.line} ({application.heading}): "
                f"`record_format` must be {FORMAT}"
            )

    substantive = [
        block
        for block in bound
        if block.value("kind") in {"purpose", "outcome", "task"}
    ]
    for block in substantive:
        if not block.value("source_statement") and not block.value("instance_statement"):
            errors.append(
                f"line {block.line} ({block.heading}): "
                "`source_statement` or `instance_statement` is required"
            )

    outcomes = [block for block in bound if block.value("kind") == "outcome"]
    criteria = [block for block in bound if block.value("kind") == "success_criterion"]
    for block in criteria:
        require(block, ("criterion",), errors)
    if not outcomes and not criteria:
        errors.append("at least one `outcome` or `success_criterion` block is required")

    tailorings = [item for item in bound if item.value("kind") == "tailoring"]
    for block in tailorings:
        require(
            block,
            (
                "basis",
                "candidate_evaluation",
                "decision",
                "affected_party_input",
                "controls_constraints",
            ),
            errors,
        )

    conformances = [item for item in bound if item.value("kind") == "conformance"]
    for block in conformances:
        require(block, ("subject", "scope", "basis", "claim", "evidence"), errors)
        claim = block.value("claim")
        if claim and claim not in {"Full", "Tailored"}:
            errors.append(
                f"line {block.line} ({block.heading}): "
                "`claim` must be `Full` or `Tailored`"
            )
        if claim == "Tailored":
            require(block, ("remaining_requirements",), errors)
            tailoring_decision = block.value("tailoring_decision")
            if not tailoring_decision and not tailorings:
                errors.append(
                    f"line {block.line} ({block.heading}): "
                    "a Tailored claim requires either a local `tailoring` block "
                    "or a `tailoring_decision` reference"
                )

    handoffs = [item for item in bound if item.value("kind") == "handoff"]
    for block in handoffs:
        require(block, ("provider", "output", "receiver", "input", "correspondence"), errors)
        if at == "completion":
            require(block, ("status",), errors)

    if at == "completion":
        for block in bound:
            if block.value("kind") in {"outcome", "success_criterion", "task"} or block.value(
                "criterion"
            ):
                require(block, ("result", "assessment"), errors)

    return errors


def command_new(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    try:
        text = render_record(args)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        output_text = one_line(args.output, "--output")
    except ValueError as exc:
        parser.error(str(exc))
    output = Path(output_text)
    if output.is_symlink():
        parser.error(f"refusing to write through a symbolic link: {output}")
    payload = text.encode("utf-8")
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
        )
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if args.force:
            if output.is_symlink():
                parser.error(f"refusing to write through a symbolic link: {output}")
            os.replace(temporary_name, output)
            temporary_name = None
        else:
            os.link(temporary_name, output)
            os.unlink(temporary_name)
            temporary_name = None
    except FileExistsError:
        parser.error(f"output already exists: {output}; use --force to replace it")
    except OSError as exc:
        parser.error(f"cannot write {output}: {exc}")
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    print(f"{LOCALES[args.locale]['created']}: {output}")
    return 0


def command_check(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    path = Path(args.record)
    try:
        errors = check_record(path, args.at)
    except (OSError, UnicodeError) as exc:
        parser.error(f"cannot read {path}: {exc}")
    if errors:
        for error in errors:
            print(f"{LOCALES[args.locale]['error']}: {error}", file=sys.stderr)
        return 1
    print(
        LOCALES[args.locale]["valid"].format(
            format=FORMAT, at=args.at, path=path
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or check a human-readable Markdown Process Instance record."
    )
    parser.add_argument("--locale", choices=tuple(LOCALES), default="en")
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="create a record from explicitly supplied statements")
    new.add_argument("--title", required=True)
    new.add_argument("--source", required=True, help="managed source and version; not a file to parse")
    new.add_argument("--context", required=True)
    new.add_argument("--scope", required=True)
    new.add_argument("--purpose", action="append", default=[], help="exact source statement; repeatable")
    new.add_argument("--outcome", action="append", default=[], help="exact source statement; repeatable")
    new.add_argument("--task", action="append", default=[], help="exact source statement; repeatable")
    new.add_argument("--criterion", action="append", default=[], help="Instance-specific success criterion; repeatable")
    new.add_argument("--output", required=True)
    new.add_argument("--force", action="store_true", help="replace an existing output file")
    new.set_defaults(handler=command_new)

    check = commands.add_parser("check", help="check the Markdown binding, not its truth or Conformance")
    check.add_argument("--at", required=True, choices=("instantiation", "completion"))
    check.add_argument("record")
    check.set_defaults(handler=command_check)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
