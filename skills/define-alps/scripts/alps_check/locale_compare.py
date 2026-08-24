"""Compare two already-parsed locale IRs without touching their source text."""

from __future__ import annotations

from .model import Diagnostic, DocumentIR, Reference, Severity, Span, deterministic_diagnostics


_Key = str | tuple[str, ...]


def _present(value: str | None) -> bool:
    return value is not None and value != ""


def _reference_identity(
    reference: Reference | None, package_identity: str | None = None
) -> str | None:
    """Return the semantic reference key while retaining lexical IR fields.

    A short reference has no package in its lexical token.  The caller may
    supply the package containing both locale assets; that context is the
    locale-comparison equivalent of the resolver's canonical identity.
    """
    if reference is None or not _present(reference.token):
        return None
    skill_name = getattr(reference, "skill_name", None)
    if not _present(skill_name):
        return reference.token
    package = reference.package_id if _present(reference.package_id) else package_identity
    return f"{package}#{skill_name}" if _present(package) else f"#{skill_name}"


def _ref_key(
    refs: tuple[Reference, ...], package_identity: str | None = None
) -> _Key | None:
    values = tuple(
        value for ref in refs
        if (value := _reference_identity(ref, package_identity)) is not None
    )
    if not values or len(values) != len(refs):
        return None
    return values[0] if len(values) == 1 else values  # type: ignore[return-value]


def _operative_ref_key(
    refs: tuple[Reference, ...], package_identity: str | None = None
) -> tuple[str, ...]:
    return tuple(
        value for ref in refs
        if (value := _reference_identity(ref, package_identity)) is not None
    )


def _loc(item: object) -> tuple[int | None, Span | None]:
    return getattr(item, "line", None), getattr(item, "span", None)


def _at(
    doc: DocumentIR, items: tuple[object, ...], index: int = 0
) -> tuple[int | None, Span | None]:
    if items:
        return _loc(items[min(index, len(items) - 1)])
    frontmatter = doc.frontmatter
    return (frontmatter.name_line, frontmatter.name_span) if frontmatter else (None, None)


def _emit(
    out: list[Diagnostic],
    doc: DocumentIR,
    code: str,
    severity: Severity,
    message: str,
    line: int | None,
    span: Span | None = None,
    reference: Reference | None = None,
) -> None:
    class_name = "locale-mismatch" if severity == Severity.ERROR else "unverified-locale-identity"
    out.append(Diagnostic(class_name, code, severity, doc.path, line, message, span, reference))


def _count(
    out: list[Diagnostic],
    english: DocumentIR,
    japanese: DocumentIR,
    left: tuple[object, ...],
    right: tuple[object, ...],
    code: str,
    label: str,
) -> None:
    if len(left) == len(right):
        return
    target, items = (japanese, right) if len(right) > len(left) else (english, left)
    line, span = _at(target, items, min(len(left), len(right)))
    _emit(out, target, code, Severity.ERROR, f"{label} count differs between locales", line, span)


def _compare(
    out: list[Diagnostic],
    english: DocumentIR,
    japanese: DocumentIR,
    left: _Key | None,
    right: _Key | None,
    left_fallback: str | None,
    right_fallback: str | None,
    left_line: int | None,
    right_line: int | None,
    code: str,
    label: str,
    left_span: Span | None = None,
    right_span: Span | None = None,
    left_ref: Reference | None = None,
    right_ref: Reference | None = None,
) -> None:
    left_fallback = left_fallback if _present(left_fallback) else None
    right_fallback = right_fallback if _present(right_fallback) else None
    if left is not None and right is not None:
        if left != right:
            _emit(out, japanese, code, Severity.ERROR, f"{label} identity/order differs",
                  right_line, right_span, right_ref)
        return
    if left is None:
        target, line, span, ref = english, left_line, left_span, left_ref
    else:
        target, line, span, ref = japanese, right_line, right_span, right_ref
    if left_fallback is not None or right_fallback is not None:
        _emit(out, target, "unverified-locale-identity", Severity.WARNING,
              f"{label} uses an unverified display identity", line, span, ref)
    else:
        _emit(out, target, "missing-stable-identity", Severity.WARNING,
              f"{label} has no stable identity", line, span, ref)


def _scalar(
    out: list[Diagnostic],
    english: DocumentIR,
    japanese: DocumentIR,
    left: str | None,
    right: str | None,
    left_line: int | None,
    right_line: int | None,
    mismatch: str,
    missing: str,
    label: str,
    left_span: Span | None = None,
    right_span: Span | None = None,
) -> None:
    left = left if _present(left) else None
    right = right if _present(right) else None
    if left is not None and right is not None:
        if left != right:
            _emit(out, japanese, mismatch, Severity.ERROR, f"{label} differs", right_line, right_span)
        return
    target, line, span = (english, left_line, left_span) if left is None else (japanese, right_line, right_span)
    _emit(out, target, missing, Severity.WARNING, f"{label} is missing", line, span)


def _process_key(
    process: object, package_identity: str | None = None
) -> tuple[_Key | None, str | None, Reference | None]:
    reference = getattr(process, "reference", None)
    key = _reference_identity(reference, package_identity)
    name = getattr(process, "name", None)
    return key, name if key is None and _present(name) else None, reference


def _outcome_key(
    outcome: object, package_identity: str | None = None
) -> tuple[_Key | None, str | None, Reference | None]:
    refs = getattr(outcome, "references", ())
    key, first = _ref_key(refs, package_identity), refs[0] if refs else None
    if key is not None:
        return key, None, first
    identity = getattr(outcome, "identity", None)
    return identity if _present(identity) else None, None, first


def _source_key(
    source: object, package_identity: str | None = None
) -> tuple[_Key | None, str | None, Reference | None]:
    reference = getattr(source, "reference", None)
    key = _reference_identity(reference, package_identity)
    name = getattr(source, "name", None)
    return key, name if key is None and _present(name) else None, reference


def _endpoint_key(
    doc: DocumentIR, value: str | None, package_identity: str | None = None
) -> tuple[_Key | None, str | None]:
    if not _present(value):
        return None, None
    matches = tuple(process for process in doc.processes if process.name == value)
    if len(matches) != 1:
        return None, None
    key = _reference_identity(matches[0].reference, package_identity)
    return (key, None) if key is not None else (None, matches[0].name)


def _relationships(
    out: list[Diagnostic],
    english: DocumentIR,
    japanese: DocumentIR,
    prefix: str,
    package_identity: str | None = None,
) -> None:
    _count(out, english, japanese, english.relationships, japanese.relationships,
           f"{prefix}-relationship-count-mismatch", "relationship")
    for index, (left, right) in enumerate(zip(english.relationships, japanese.relationships)):
        l_line, l_span, r_line, r_span = (*_loc(left), *_loc(right))
        for field, label in (("provider_process", "provider"), ("recipient_process", "recipient")):
            l_key, l_fallback = _endpoint_key(english, getattr(left, field), package_identity)
            r_key, r_fallback = _endpoint_key(japanese, getattr(right, field), package_identity)
            _compare(out, english, japanese, l_key, r_key, l_fallback, r_fallback,
                     l_line, r_line, f"{prefix}-relationship-{label}-mismatch",
                     f"relationship {label} at position {index + 1}", l_span, r_span)


def _entries(
    out: list[Diagnostic],
    english: DocumentIR,
    japanese: DocumentIR,
    prefix: str,
    centers: bool = False,
    package_identity: str | None = None,
) -> None:
    _count(out, english, japanese, english.processes, japanese.processes,
           f"{prefix}-process-count-mismatch", "process")
    for index, (left, right) in enumerate(zip(english.processes, japanese.processes)):
        l_line, l_span, r_line, r_span = (*_loc(left), *_loc(right))
        l_key, l_fallback, l_ref = _process_key(left, package_identity)
        r_key, r_fallback, r_ref = _process_key(right, package_identity)
        _compare(out, english, japanese, l_key, r_key, l_fallback, r_fallback, l_line, r_line,
                 f"{prefix}-process-identity-mismatch", f"process at position {index + 1}",
                 l_span, r_span, l_ref, r_ref)
        if not centers:
            continue
        _count(out, english, japanese, left.outcomes, right.outcomes,
               f"{prefix}-semantic-center-count-mismatch", "semantic center")
        for center_index, (l_center, r_center) in enumerate(zip(left.outcomes, right.outcomes)):
            ll, ls, rl, rs = (*_loc(l_center), *_loc(r_center))
            lk = _operative_ref_key(l_center.references, package_identity)
            rk = _operative_ref_key(r_center.references, package_identity)
            lr = l_center.references[0] if l_center.references else None
            rr = r_center.references[0] if r_center.references else None
            _compare(out, english, japanese, lk, rk, None, None, ll, rl,
                     f"{prefix}-semantic-center-mismatch",
                     f"semantic center {center_index + 1} of process {index + 1}", ls, rs, lr, rr)


def _process(
    english: DocumentIR, japanese: DocumentIR, out: list[Diagnostic], package_identity: str | None = None
) -> None:
    _count(out, english, japanese, english.outcomes, japanese.outcomes,
           "process-outcome-count-mismatch", "outcome")
    for index, (left, right) in enumerate(zip(english.outcomes, japanese.outcomes)):
        ll, ls, rl, rs = (*_loc(left), *_loc(right))
        _compare(out, english, japanese, _operative_ref_key(left.references, package_identity),
                 _operative_ref_key(right.references, package_identity),
                 None, None, ll, rl, "process-outcome-reference-mismatch",
                 f"outcome reference sequence at position {index + 1}", ls, rs,
                 left.references[0] if left.references else None, right.references[0] if right.references else None)
    _count(out, english, japanese, english.activities, japanese.activities,
           "process-activity-count-mismatch", "activity")
    for activity_index, (left, right) in enumerate(zip(english.activities, japanese.activities)):
        _count(out, english, japanese, left.tasks, right.tasks, "process-task-count-mismatch",
               f"task count for activity {activity_index + 1}")
        for task_index, (l_task, r_task) in enumerate(zip(left.tasks, right.tasks)):
            ll, ls, rl, rs = (*_loc(l_task), *_loc(r_task))
            _scalar(out, english, japanese, l_task.normative_class, r_task.normative_class,
                    ll, rl, "process-task-normative-class-mismatch", "missing-normative-class",
                    f"normative class for task {task_index + 1}", ls, rs)


def _applications(
    out: list[Diagnostic], english: DocumentIR, japanese: DocumentIR, package_identity: str | None = None
) -> None:
    _count(out, english, japanese, english.application, japanese.application,
           "reference-semantic-center-count-mismatch", "semantic center")
    for index, (left, right) in enumerate(zip(english.application, japanese.application)):
        ll, ls, rl, rs = (*_loc(left), *_loc(right))
        lk, rk = _ref_key(left.references, package_identity), _ref_key(right.references, package_identity)
        _compare(out, english, japanese, lk, rk,
                 left.text if lk is None else None, right.text if rk is None else None,
                 ll, rl, "reference-semantic-center-mismatch", f"semantic center {index + 1}", ls, rs,
                 left.references[0] if left.references else None, right.references[0] if right.references else None)


def _reference_model(
    english: DocumentIR, japanese: DocumentIR, out: list[Diagnostic], package_identity: str | None = None
) -> None:
    has_applications = bool(english.application or japanese.application)
    _entries(out, english, japanese, "reference", centers=not has_applications,
             package_identity=package_identity)
    if has_applications:
        _applications(out, english, japanese, package_identity)
    _relationships(out, english, japanese, "reference", package_identity)


def _view(
    english: DocumentIR, japanese: DocumentIR, out: list[Diagnostic], package_identity: str | None = None
) -> None:
    _count(out, english, japanese, english.outcomes, japanese.outcomes, "view-outcome-count-mismatch", "outcome")
    for index, (left, right) in enumerate(zip(english.outcomes, japanese.outcomes)):
        ll, ls, rl, rs = (*_loc(left), *_loc(right))
        lk, lf, lr = _outcome_key(left, package_identity)
        rk, rf, rr = _outcome_key(right, package_identity)
        _compare(out, english, japanese, lk, rk, lf, rf, ll, rl,
                 "view-outcome-identity-mismatch", f"outcome {index + 1}", ls, rs, lr, rr)
    _count(out, english, japanese, english.source_processes, japanese.source_processes,
           "view-source-process-count-mismatch", "source process")
    for index, (left, right) in enumerate(zip(english.source_processes, japanese.source_processes)):
        ll, ls, rl, rs = (*_loc(left), *_loc(right))
        lk, lf, lr = _source_key(left, package_identity)
        rk, rf, rr = _source_key(right, package_identity)
        _compare(out, english, japanese, lk, rk, lf, rf, ll, rl,
                 "view-source-reference-mismatch", f"source process {index + 1}", ls, rs, lr, rr)
    _count(out, english, japanese, english.included_activities_tasks, japanese.included_activities_tasks,
           "view-included-count-mismatch", "included activity/task")
    for index, (left, right) in enumerate(zip(english.included_activities_tasks, japanese.included_activities_tasks)):
        ll, ls, rl, rs = (*_loc(left), *_loc(right))
        _scalar(out, english, japanese, left.kind, right.kind, ll, rl,
                "view-included-kind-mismatch", "missing-included-kind", f"included kind {index + 1}", ls, rs)
        lk = _reference_identity(left.source_reference, package_identity)
        rk = _reference_identity(right.source_reference, package_identity)
        _compare(out, english, japanese, lk, rk,
                 left.source_display if lk is None else None, right.source_display if rk is None else None,
                 ll, rl, "view-included-source-reference-mismatch", f"included source {index + 1}", ls, rs,
                 left.source_reference, right.source_reference)


def _frontmatter(english: DocumentIR, japanese: DocumentIR, out: list[Diagnostic]) -> None:
    left, right = english.frontmatter, japanese.frontmatter
    ln, rn = (left.name if left else None), (right.name if right else None)
    _compare(out, english, japanese, ln if _present(ln) else None, rn if _present(rn) else None,
             None, None, left.name_line if left else None, right.name_line if right else None,
             "frontmatter-name-mismatch", "frontmatter name", left.name_span if left else None,
             right.name_span if right else None)
    lk, rk = (left.kind if left else None), (right.kind if right else None)
    _scalar(out, english, japanese, lk, rk, left.kind_line if left else None, right.kind_line if right else None,
            "frontmatter-kind-mismatch", "missing-frontmatter-kind", "frontmatter kind",
            left.kind_span if left else None, right.kind_span if right else None)


def compare_locale_ir(
    english: DocumentIR,
    japanese: DocumentIR,
    package_identity: str | None = None,
) -> tuple[Diagnostic, ...]:
    """Compare locale IRs, normalizing short refs with the containing package."""
    out: list[Diagnostic] = []
    _frontmatter(english, japanese, out)
    left_kind = english.frontmatter.kind if english.frontmatter else english.kind
    right_kind = japanese.frontmatter.kind if japanese.frontmatter else japanese.kind
    if left_kind == right_kind:
        if left_kind == "process":
            _process(english, japanese, out, package_identity)
        elif left_kind == "process-model":
            _entries(out, english, japanese, "model", package_identity=package_identity)
            _relationships(out, english, japanese, "model", package_identity)
        elif left_kind == "process-reference-model":
            _reference_model(english, japanese, out, package_identity)
        elif left_kind == "process-view":
            _view(english, japanese, out, package_identity)
    return deterministic_diagnostics(out)
