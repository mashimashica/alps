"""Semantic validation over typed ALPS IR; no source-text access is allowed."""
from __future__ import annotations
from pathlib import Path
from typing import Callable
try:
    from .model import (MAX_RECORDS_PER_SECTION, Diagnostic, DocumentIR, ParseResult,
                        Reference, Severity, deterministic_diagnostics)
    from .reference_profile import localized_target, resolve_reference
except ImportError:  # pragma: no cover
    from model import (MAX_RECORDS_PER_SECTION, Diagnostic, DocumentIR, ParseResult,
                       Reference, Severity, deterministic_diagnostics)  # type: ignore
    from reference_profile import localized_target, resolve_reference  # type: ignore
IR_ONLY = True
LoadIR = Callable[[Path, str | None], ParseResult | DocumentIR | None]

def _is_ja(locale: str | None) -> bool:
    return isinstance(locale, str) and locale.lower().split("-", 1)[0] == "ja"

def _diag(ir, code, message, *, line=None, class_name="semantic", severity=Severity.ERROR,
          path=None, reference=None):
    return Diagnostic(class_name, code, severity, str(path if path is not None else ir.path),
                      line, message, reference=reference)

def _bounded(items, label, path, diagnostics, seen):
    key = (id(items), label, str(path))
    if len(items) > MAX_RECORDS_PER_SECTION and key not in seen:
        item = items[MAX_RECORDS_PER_SECTION]
        diagnostics.append(Diagnostic("profile-structure", "record-limit", Severity.ERROR,
            str(path), getattr(item, "line", None),
            f"{label} section exceeds {MAX_RECORDS_PER_SECTION} records"))
        seen.add(key)
    return items[:MAX_RECORDS_PER_SECTION]

def _rkey(reference: Reference):
    return reference.token, reference.skill_name, reference.package_id


def _resolved_identity(reference: Reference | None, resolutions) -> str | None:
    """Return the filesystem-resolved identity, never the lexical token."""
    if not isinstance(reference, Reference):
        return None
    result = resolutions.get(_rkey(reference))
    if result is None or result.resolved is None:
        return None
    return result.resolved.identity


def _resolved_declaration_duplicates(
    entries, resolutions, ir, diagnostics, *, message: str
) -> None:
    """Report canonical duplicate declarations while preserving raw IR spans."""
    seen_identity = {}
    seen_raw = set()
    for entry in entries:
        reference = entry.reference
        raw = _rkey(reference) if isinstance(reference, Reference) else None
        raw_duplicate = raw is not None and raw in seen_raw
        if raw is not None:
            seen_raw.add(raw)
        identity = _resolved_identity(reference, resolutions)
        if identity is None:
            continue
        previous = seen_identity.get(identity)
        if previous is not None and not raw_duplicate:
            diagnostics.append(_diag(
                ir,
                "process-duplicate",
                message,
                line=entry.line,
                class_name="semantic",
                reference=reference,
            ))
        else:
            seen_identity.setdefault(identity, entry)


def _okey(outcome, path, diagnostics, limits):
    refs = _bounded(outcome.references, "Outcome references", path, diagnostics, limits)
    return outcome.text, outcome.identity, tuple(x.token for x in refs if isinstance(x, Reference))

def validate_ir(ir: DocumentIR, configured_roots, *, current_package_id: str | None = None,
                load_ir: LoadIR) -> tuple[Diagnostic, ...]:
    """Validate one already-parsed document and its IR-resolved dependencies."""
    if not isinstance(ir, DocumentIR):
        raise TypeError("validate_ir requires a DocumentIR")
    diagnostics = []
    limits = set()
    outcomes = _bounded(ir.outcomes, "Outcomes", ir.path, diagnostics, limits)
    activities = _bounded(ir.activities, "Activities", ir.path, diagnostics, limits)
    processes = _bounded(ir.processes, "Processes", ir.path, diagnostics, limits)
    relationships = _bounded(ir.relationships, "Relationships", ir.path, diagnostics, limits)
    sources = _bounded(ir.source_processes, "Source Processes", ir.path, diagnostics, limits)
    inclusions = _bounded(ir.included_activities_tasks, "Included Activities and Tasks", ir.path, diagnostics, limits)
    applications = _bounded(ir.application, "Application", ir.path, diagnostics, limits)
    if ir.kind == "process" and ir.frontmatter is not None:
        suffix = "ALPS準拠。" if _is_ja(ir.locale) else "ALPS-conformant."
        if not ir.frontmatter.description.endswith(suffix):
            diagnostics.append(_diag(ir, "description-suffix",
                f"Process description must end in {suffix}", line=ir.frontmatter.description_line,
                class_name="profile-structure"))

    references = []
    reference_keys = set()
    reference_overflow = False
    def add_reference(value):
        nonlocal reference_overflow
        if not isinstance(value, Reference):
            if value is not None:
                diagnostics.append(_diag(ir, "invalid-reference-ir", "IR reference is not a Reference",
                                         class_name="internal"))
            return
        key = _rkey(value)
        if key in reference_keys:
            return
        if len(references) >= MAX_RECORDS_PER_SECTION:
            reference_overflow = True
            return
        reference_keys.add(key)
        references.append(value)
    for ref in _bounded(ir.references, "References", ir.path, diagnostics, limits):
        add_reference(ref)
    for outcome in outcomes:
        for ref in _bounded(outcome.references, "Outcome references", ir.path, diagnostics, limits):
            add_reference(ref)
    for activity in activities:
        for task in _bounded(activity.tasks, "Tasks", ir.path, diagnostics, limits):
            for ref in _bounded(task.references, "Task references", ir.path, diagnostics, limits):
                add_reference(ref)
    for entry in processes:
        add_reference(entry.reference)
        for outcome in _bounded(entry.outcomes, "Outcomes", ir.path, diagnostics, limits):
            for ref in _bounded(outcome.references, "Outcome references", ir.path, diagnostics, limits):
                add_reference(ref)
    for source in sources:
        add_reference(source.reference)
    for inclusion in inclusions:
        add_reference(inclusion.source_reference)
    for application in applications:
        for ref in _bounded(application.references, "Application references", ir.path, diagnostics, limits):
            add_reference(ref)
    if reference_overflow:
        diagnostics.append(_diag(ir, "reference-limit", f"IR references exceed {MAX_RECORDS_PER_SECTION} records",
                                 class_name="profile-structure"))

    resolutions = {}
    for ref in references:
        key = _rkey(ref)
        try:
            result = resolve_reference(ref, configured_roots, containing_path=ir.path,
                                      current_package_id=current_package_id)
        except Exception as error:
            diagnostics.append(_diag(ir, "reference-resolution", f"reference resolver failed: {error}",
                                     line=ref.line, class_name="internal", reference=ref))
            resolutions[key] = None
            continue
        diagnostics.extend(result.diagnostics)
        resolutions[key] = result

    target_cache = {}
    def target_for(ref):
        result = resolutions.get(_rkey(ref))
        if result is None or result.resolved is None:
            return None, False
        resolved = result.resolved
        cache_key = (resolved.identity, ir.locale)
        if cache_key in target_cache:
            return target_cache[cache_key]
        selected = []
        try:
            target_path = localized_target(result, ir.locale, diagnostics=selected)
        except Exception as error:
            diagnostics.append(_diag(ir, "localized-target", f"localized target selection failed: {error}",
                                     line=ref.line, class_name="internal", reference=ref))
            target_cache[cache_key] = (None, False)
            return target_cache[cache_key]
        diagnostics.extend(selected)
        if target_path is None:
            diagnostics.append(_diag(ir, "target-not-selected", "reference has no target path",
                                     line=ref.line, reference=ref))
            target_cache[cache_key] = (None, False)
            return target_cache[cache_key]
        target_locale = "ja" if target_path != resolved.target else None
        try:
            loaded = load_ir(target_path, target_locale)
        except Exception as error:
            diagnostics.append(_diag(ir, "target-load-failed", f"target IR loader failed: {error}",
                                     line=ref.line, class_name="internal", path=target_path, reference=ref))
            target_cache[cache_key] = (None, False)
            return target_cache[cache_key]
        target_diagnostics = loaded.diagnostics if isinstance(loaded, ParseResult) else ()
        diagnostics.extend(target_diagnostics)
        target = loaded if isinstance(loaded, DocumentIR) else loaded.ir if isinstance(loaded, ParseResult) else None
        failed = target is None or (isinstance(loaded, ParseResult) and
                                    (loaded.ir is None or any(x.severity is Severity.ERROR for x in target_diagnostics)))
        if failed:
            diagnostics.append(_diag(ir, "target-parse-failed",
                "referenced target did not produce a valid Process IR", line=ref.line,
                class_name="semantic", path=target_path, reference=ref))
            target_cache[cache_key] = (None, False)
            return target_cache[cache_key]
        comparable = not _is_ja(ir.locale) or target_locale == "ja"
        target_cache[cache_key] = (target, comparable)
        return target_cache[cache_key]

    def require_process(target, ref, line):
        if target.kind != "process":
            diagnostics.append(_diag(ir, "reference-target-kind", "reference target must be a Process",
                                     line=line, reference=ref))
            return False
        return True

    if ir.kind in ("process-model", "process-reference-model"):
        declared = {entry.name for entry in processes}
        for relationship in relationships:
            if relationship.provider_process not in declared or relationship.recipient_process not in declared:
                diagnostics.append(_diag(ir, "relationship-endpoint",
                    "relationship endpoints must be declared Process entries", line=relationship.line))
    if ir.kind == "process-model":
        _resolved_declaration_duplicates(
            processes,
            resolutions,
            ir,
            diagnostics,
            message="Process display names and resolved identities must be unique",
        )
        for entry in processes:
            if not isinstance(entry.reference, Reference):
                continue
            target, comparable = target_for(entry.reference)
            if target is None or not require_process(target, entry.reference, entry.line):
                continue
            if comparable and entry.name != target.h1_title:
                diagnostics.append(_diag(ir, "reference-display",
                    "Process display name must equal the target H1", line=entry.line, reference=entry.reference))
    if ir.kind == "process-reference-model":
        _resolved_declaration_duplicates(
            processes,
            resolutions,
            ir,
            diagnostics,
            message="Reference Model Process names and resolved identities must be unique",
        )
        for entry in processes:
            if not isinstance(entry.reference, Reference):
                continue
            target, comparable = target_for(entry.reference)
            if target is None or not require_process(target, entry.reference, entry.line) or not comparable:
                continue
            if entry.name != target.h1_title:
                diagnostics.append(_diag(ir, "reference-name", "Process entry Name must equal the target H1",
                                          line=entry.line, reference=entry.reference))
            if entry.purpose != target.purpose:
                diagnostics.append(_diag(ir, "reference-purpose",
                    "Process entry Purpose must equal the target Process Purpose", line=entry.line, reference=entry.reference))
            expected = tuple(_okey(x, target.path, diagnostics, limits) for x in
                             _bounded(target.outcomes, "Outcomes", target.path, diagnostics, limits))
            actual = tuple(_okey(x, ir.path, diagnostics, limits) for x in
                           _bounded(entry.outcomes, "Outcomes", ir.path, diagnostics, limits))
            if actual != expected:
                diagnostics.append(_diag(ir, "reference-outcomes",
                    "Process entry Outcomes must equal the target Process Outcomes", line=entry.line, reference=entry.reference))
    if ir.kind == "process-view":
        by_identity = {}
        by_raw = {}
        names = set()
        raw_references = set()
        resolved_identities = set()
        for source in sources:
            ref = source.reference
            raw = _rkey(ref) if isinstance(ref, Reference) else None
            raw_duplicate = raw is not None and raw in raw_references
            display_duplicate = source.name in names
            if display_duplicate or raw_duplicate:
                diagnostics.append(_diag(ir, "source-duplicate",
                    "Source Process names and references must be unique", line=source.line))
            names.add(source.name)
            if raw is not None:
                raw_references.add(raw)
                by_raw.setdefault(raw, source)
            identity = _resolved_identity(ref, resolutions)
            if identity is not None:
                if identity in resolved_identities and not (display_duplicate or raw_duplicate):
                    diagnostics.append(_diag(
                        ir,
                        "source-duplicate",
                        "Source Process names and resolved identities must be unique",
                        line=source.line,
                        reference=ref,
                    ))
                resolved_identities.add(identity)
                by_identity.setdefault(identity, source)
            if not isinstance(ref, Reference):
                diagnostics.append(_diag(ir, "source-reference", "Source Process must have a Skill reference",
                                         line=source.line))
                continue
            target, comparable = target_for(ref)
            if target is None or not require_process(target, ref, source.line):
                continue
            if comparable and source.name != target.h1_title:
                diagnostics.append(_diag(ir, "source-display",
                    "Source Process display name must equal the target H1", line=source.line, reference=ref))
        included_keys = set()
        for inclusion in inclusions:
            ref = inclusion.source_reference
            raw = _rkey(ref) if isinstance(ref, Reference) else None
            identity = _resolved_identity(ref, resolutions)
            declared = by_identity.get(identity) if identity is not None else by_raw.get(raw)
            same_reference = False
            if declared is not None and isinstance(declared.reference, Reference) and isinstance(ref, Reference):
                declared_identity = _resolved_identity(declared.reference, resolutions)
                if identity is not None and declared_identity is not None:
                    same_reference = identity == declared_identity
                else:
                    same_reference = _rkey(ref) == _rkey(declared.reference)
            if (declared is None or not isinstance(declared.reference, Reference)
                    or inclusion.source_display != declared.name or not same_reference):
                diagnostics.append(_diag(ir, "included-source",
                    "Included source must bind the exact declared Source Process identity",
                    line=inclusion.line, reference=ref if isinstance(ref, Reference) else None))
            identity_key = ("resolved", identity) if identity is not None else ("raw", raw)
            key = (identity_key, inclusion.kind, inclusion.label)
            if identity_key[1] is not None and key in included_keys:
                diagnostics.append(_diag(ir, "included-duplicate",
                    "Included Activity/Task identity is duplicated", line=inclusion.line))
            if identity_key[1] is not None:
                included_keys.add(key)
    return deterministic_diagnostics(diagnostics)
