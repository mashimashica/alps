"""Narrow physical-format, link and Python syntax check; not the official validator."""
import ast
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1] / "deliverables/skills/reimbursement-ledger-rollup"
text = (root / "SKILL.md").read_text()
assert text.startswith("---\n")
front = text.split("---\n", 2)[1]
fields = dict(line.split(": ", 1) for line in front.strip().splitlines())
assert fields["name"] == root.name
assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"])
assert len(fields["name"]) <= 64
assert 0 < len(fields["description"]) <= 1024
assert 0 < len(fields["compatibility"]) <= 500
assert len(text.splitlines()) < 500
for target in re.findall(r"\]\(([^)]+)\)", text):
    assert (root / target.split("#")[0]).is_file(), target
ast.parse((root / "scripts/rollup.py").read_text())
print("PASS: required frontmatter, naming/length constraints, packaged file links, Python syntax")
