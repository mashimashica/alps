#!/usr/bin/env python3
"""Report passive structural facts about one or more SVG files.

This script does not assess visual fidelity, aesthetic quality, rights, safety in a
specific consumer, or ALPS Conformance. It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


COUNTED_ELEMENTS = (
    "svg",
    "g",
    "path",
    "rect",
    "circle",
    "ellipse",
    "line",
    "polyline",
    "polygon",
    "text",
    "use",
    "defs",
    "linearGradient",
    "radialGradient",
    "pattern",
    "clipPath",
    "mask",
    "filter",
    "image",
    "script",
    "foreignObject",
)

HREF_NAMES = {
    "href",
    "{http://www.w3.org/1999/xlink}href",
}


def local_name(tag: str) -> str:
    """Return an XML local name without its namespace."""
    return tag.rsplit("}", 1)[-1]


def classify_reference(value: str) -> str:
    """Classify an href-like value without resolving or fetching it."""
    stripped = value.strip()
    if not stripped:
        return "empty"
    if stripped.startswith("#"):
        return "internal-fragment"
    if stripped.startswith("data:"):
        return "embedded-data"
    parsed = urlparse(stripped)
    if parsed.scheme or parsed.netloc:
        return "external-url"
    return "relative-reference"


def inspect_svg(path: Path) -> dict[str, Any]:
    """Parse an SVG and return facts that can be observed mechanically."""
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError) as exc:
        return {
            "path": str(path),
            "ok": False,
            "error": str(exc),
        }

    root = tree.getroot()
    elements = list(root.iter())
    names = [local_name(element.tag) for element in elements]
    counts = Counter(names)

    ids: list[str] = []
    group_ids: list[str] = []
    event_handler_attributes: list[dict[str, str]] = []
    references: list[dict[str, str]] = []

    for element in elements:
        element_name = local_name(element.tag)
        element_id = element.attrib.get("id")
        if element_id:
            ids.append(element_id)
            if element_name == "g":
                group_ids.append(element_id)

        for attribute_name, value in element.attrib.items():
            attribute_local_name = local_name(attribute_name)
            if attribute_local_name.lower().startswith("on"):
                event_handler_attributes.append(
                    {
                        "element": element_name,
                        "id": element_id or "",
                        "attribute": attribute_local_name,
                    }
                )
            if attribute_name in HREF_NAMES or attribute_local_name == "href":
                references.append(
                    {
                        "element": element_name,
                        "id": element_id or "",
                        "value": value,
                        "kind": classify_reference(value),
                    }
                )

    duplicate_ids = sorted(
        element_id for element_id, count in Counter(ids).items() if count > 1
    )

    report: dict[str, Any] = {
        "path": str(path),
        "ok": True,
        "root_element": local_name(root.tag),
        "width": root.attrib.get("width"),
        "height": root.attrib.get("height"),
        "viewBox": root.attrib.get("viewBox"),
        "element_count": len(elements),
        "counts": {name: counts.get(name, 0) for name in COUNTED_ELEMENTS},
        "defined_id_count": len(ids),
        "group_ids": sorted(group_ids),
        "duplicate_ids": duplicate_ids,
        "references": references,
        "embedded_raster_count": sum(
            1
            for reference in references
            if reference["element"] == "image"
            and reference["kind"] == "embedded-data"
        ),
        "external_reference_count": sum(
            1
            for reference in references
            if reference["kind"] in {"external-url", "relative-reference"}
        ),
        "event_handler_attributes": event_handler_attributes,
        "active_or_foreign_content_present": bool(
            counts.get("script", 0)
            or counts.get("foreignObject", 0)
            or event_handler_attributes
        ),
    }
    return report


def format_text(report: dict[str, Any]) -> str:
    """Render a concise human-readable report."""
    if not report.get("ok"):
        return f"{report['path']}: ERROR: {report['error']}"

    lines = [
        f"path: {report['path']}",
        f"root: {report['root_element']}",
        (
            f"dimensions: width={report['width']!r} "
            f"height={report['height']!r} "
            f"viewBox={report['viewBox']!r}"
        ),
        f"elements: {report['element_count']}",
    ]
    nonzero_counts = [
        f"{name}={count}"
        for name, count in report["counts"].items()
        if count
    ]
    lines.append("counts: " + ", ".join(nonzero_counts))
    lines.append(f"group ids: {', '.join(report['group_ids']) or '(none)'}")
    lines.append(
        f"duplicate ids: {', '.join(report['duplicate_ids']) or '(none)'}"
    )
    lines.append(f"references: {len(report['references'])}")
    lines.append(f"embedded raster references: {report['embedded_raster_count']}")
    lines.append(
        "external or relative references: "
        f"{report['external_reference_count']}"
    )
    lines.append(
        f"event-handler attributes: {len(report['event_handler_attributes'])}"
    )
    lines.append(
        "active or foreign content present: "
        f"{str(report['active_or_foreign_content_present']).lower()}"
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report passive structural facts about SVG files. The report does not "
            "establish visual fidelity, aesthetic quality, rights, or ALPS Conformance."
        )
    )
    parser.add_argument("svg", nargs="+", type=Path, help="SVG file to inspect")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a JSON array instead of human-readable text",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    reports = [inspect_svg(path) for path in args.svg]

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("\n\n".join(format_text(report) for report in reports))

    return 0 if all(report.get("ok") for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
