#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

BINDING = "alps-markdown-agent-plugins/1.0"
MODEL_KINDS = {"process-model", "process-reference-model"}
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)")
COMPARATOR = re.compile(r"^(>=|<=|==|=|>|<)(\d+\.\d+\.\d+)$")

@dataclass
class Asset:
    kind: str; id: str; name: str; version: str; status: str; path: str; compatible: bool; issues: list[str]; resolved_sources: list[dict[str, str]]

def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"): raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0: raise ValueError("unterminated frontmatter")
    front = {}
    for raw in text[4:end].splitlines():
        line = raw.strip()
        if not line or line.startswith("#"): continue
        key, value = line.split(":", 1); front[key.strip()] = value.strip().strip('"').strip("'")
    return front, text[end + 5:]

def version(value: str) -> tuple[int, int, int]:
    m = SEMVER.match(value)
    if not m: raise ValueError(f"invalid semantic version: {value}")
    return tuple(int(x) for x in m.groups())

def satisfies(current_text: str, range_text: str) -> bool:
    current = version(current_text)
    for token in range_text.split():
        m = COMPARATOR.fullmatch(token)
        if not m: raise ValueError(f"unsupported range comparator: {token}")
        op, target_text = m.groups(); target = version(target_text)
        if op == ">" and not current > target: return False
        if op == ">=" and not current >= target: return False
        if op == "<" and not current < target: return False
        if op == "<=" and not current <= target: return False
        if op in {"=", "=="} and current != target: return False
    return True

def section(body: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", body, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""

def table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2: return [], []
    return [c.strip() for c in lines[0].strip("|").split("|")], [[c.strip() for c in line.strip("|").split("|")] for line in lines[2:]]

def discover(root: Path) -> list[Path]:
    paths = []
    if (root / ".alps/MODEL.md").is_file(): paths.append(root / ".alps/MODEL.md")
    paths.extend(sorted((root / ".alps/models").glob("*/MODEL.md")))
    paths.extend(sorted((root / ".alps/views").glob("*/VIEW.md")))
    return paths

def plugin_roots(values: list[str]) -> dict[str, Path]:
    result = {}
    for value in values:
        plugin_id, path = value.split("=", 1); result[plugin_id] = Path(path).resolve()
    return result

def resolve_source(source: str, root: Path, plugins: dict[str, Path], allow_unresolved: bool) -> tuple[dict[str, str], str | None]:
    if source.startswith("local:"):
        skill = (root / source.removeprefix("local:")).resolve() / "SKILL.md"
        return ({"source": source, "state": "resolved", "path": str(skill)}, None) if skill.is_file() else ({"source": source, "state": "missing"}, f"missing local Skill: {skill}")
    if source.startswith("plugin:"):
        remainder = source.removeprefix("plugin:")
        if "/" not in remainder: return {"source": source, "state": "invalid"}, "plugin source must include plugin and Skill IDs"
        plugin_id, skill_id = remainder.rsplit("/", 1); base = plugins.get(plugin_id)
        if base is None:
            return {"source": source, "state": "unresolved-accepted" if allow_unresolved else "unresolved"}, None if allow_unresolved else f"plugin root not supplied: {plugin_id}"
        skill = base / "skills" / skill_id / "SKILL.md"
        return ({"source": source, "state": "resolved", "path": str(skill)}, None) if skill.is_file() else ({"source": source, "state": "missing"}, f"missing plugin Skill: {skill}")
    if source.startswith("uri:"):
        return {"source": source, "state": "unresolved-accepted" if allow_unresolved else "unresolved"}, None if allow_unresolved else f"URI source not resolved: {source}"
    return {"source": source, "state": "invalid"}, f"unsupported source: {source}"

def resolve_asset(path: Path, root: Path, alps_version: str, plugins: dict[str, Path], allow_unresolved: bool, model_ids: set[str]) -> Asset:
    issues = []; resolved = []
    try: front, body = parse_frontmatter(path)
    except Exception as exc: return Asset("unknown", path.stem, path.stem, "0.0.0", "invalid", str(path), False, [str(exc)], [])
    kind = front.get("kind", "unknown"); asset_id = front.get("id", path.stem)
    if front.get("binding") != BINDING: issues.append(f"unsupported binding: {front.get('binding')}")
    try:
        if not satisfies(alps_version, front.get("alps-requires", "")): issues.append(f"ALPS {alps_version} does not satisfy {front.get('alps-requires')}")
    except ValueError as exc: issues.append(str(exc))
    if kind in MODEL_KINDS:
        headers, rows = table(section(body, "Included Processes"))
        if headers:
            try: source_index = headers.index("Skill Source")
            except ValueError: issues.append("Included Processes table has no Skill Source column")
            else:
                for row in rows:
                    result, issue = resolve_source(row[source_index], root, plugins, allow_unresolved); resolved.append(result)
                    if issue: issues.append(issue)
    elif kind == "process-view":
        for model_id in [x.strip() for x in front.get("source-models", "").split(",") if x.strip()]:
            state = "resolved" if model_id in model_ids else "missing"; resolved.append({"source-model": model_id, "state": state})
            if state == "missing": issues.append(f"source Model not found: {model_id}")
    else: issues.append(f"unsupported kind: {kind}")
    return Asset(kind, asset_id, front.get("name", asset_id), front.get("version", "0.0.0"), front.get("status", "unknown"), str(path.relative_to(root)), not issues, issues, resolved)

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=Path(".")); parser.add_argument("--alps-version", required=True); parser.add_argument("--plugin-root", action="append", default=[]); parser.add_argument("--allow-unresolved-external", action="store_true"); parser.add_argument("--json", action="store_true"); args = parser.parse_args()
    root = args.root.resolve(); paths = discover(root); plugins = plugin_roots(args.plugin_root)
    fronts = []; seen = {}; duplicates = []
    for path in paths:
        try: front, _ = parse_frontmatter(path)
        except Exception: front = {}
        asset_id = front.get("id", "")
        if asset_id and asset_id in seen: duplicates.append(f"duplicate asset id {asset_id}: {seen[asset_id]} and {path}")
        if asset_id: seen[asset_id] = path
        fronts.append(front)
    model_ids = {f.get("id", "") for f in fronts if f.get("kind") in MODEL_KINDS}
    assets = [resolve_asset(path, root, args.alps_version, plugins, args.allow_unresolved_external, model_ids) for path in paths]
    if duplicates and assets: assets[0].issues.extend(duplicates); assets[0].compatible = False
    if args.json: print(json.dumps([asdict(a) for a in assets], ensure_ascii=False, indent=2))
    else:
        for asset in assets:
            print(f"{asset.kind} {asset.id} {asset.version}: {'compatible' if asset.compatible else 'incompatible'} ({asset.path})")
            for issue in asset.issues: print(f"  - {issue}")
            for source in asset.resolved_sources: print(f"  - {source}")
    return 0 if assets and all(a.compatible for a in assets) else 1

if __name__ == "__main__": raise SystemExit(main())
