"""Read-only package checks; no release state or simulator operation is created."""
import ast
from pathlib import Path
import re

root = Path(__file__).resolve().parent
skill = root / "deliverables/skills/checkout-release"
main = (skill / "SKILL.md").read_text()
assert main.startswith("---\n")
front, body = main[4:].split("\n---\n", 1)
fields = dict(line.split(": ", 1) for line in front.splitlines())
assert set(fields) == {"name", "description", "compatibility"}
assert fields["name"] == skill.name
assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"])
assert 1 <= len(fields["name"]) <= 64
assert 1 <= len(fields["description"]) <= 1024
assert len(main.splitlines()) < 500
for heading in ("# Checkout Service Release", "## Purpose", "## Outcomes", "## Activities & Tasks"):
    assert heading in body
print("PASS: constrained frontmatter and required description structure")

links = 0
files = sorted(skill.rglob("*.md"))
for path in files:
    text = path.read_text()
    assert "/workspace/" not in text
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        assert not target.startswith(("http:", "https:", "/")), target
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        assert resolved.is_relative_to(skill.resolve()), target
        assert resolved.is_file(), target
        links += 1
print(f"PASS: {links} packaged links resolve in {len(files)} Markdown files; no authoring workspace paths")

source = (root / "input/release_tool.py").read_text()
tree = ast.parse(source)
assert {node.name for node in tree.body if isinstance(node, ast.FunctionDef)} == {"operate", "main"}
contract = (skill / "references/command-contract.md").read_text()
for operation in ("inspect", "qualify", "promote", "request-status", "probe", "checkout"):
    assert f'"{operation}"' in source
    assert operation in contract
for flag in ("--state", "--candidate", "--request-id"):
    assert f'"{flag}"' in source
    assert flag in contract
print("PASS: supplied Python source parses; all six documented operations and three data flags occur in source")
print("LIMIT: static checks only; no full YAML/reference validator, agent execution trial, state mutation, or production verification")
