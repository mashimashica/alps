"""Copy previously independent, unchanged cases for three C-control families.

These are reused calibration/development stimuli, not new holdouts. This creates
case banks only, not any creator-visible or consumer execution workspace.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
for family in ("S01", "S05", "S10"):
    destination = ROOT / "control-consumer-cases" / family
    oracle = ROOT / "control-oracles" / f"{family}.md"
    if destination.exists() or oracle.exists():
        raise SystemExit(f"Existing control case must be preserved: {family}")
for family in ("S01", "S05", "S10"):
    source_root = ROOT / ("consumer-source" if family == "S01" else "development-consumer-cases") / family
    for variant in ("ordinary", "challenging"):
        source = source_root / variant
        if family == "S05":
            source = source / "input"
        shutil.copytree(source, ROOT / "control-consumer-cases" / family / variant / "input")
    oracle_source = ROOT / ("oracles" if family == "S01" else "development-oracles") / f"{family}.md"
    shutil.copy2(oracle_source, ROOT / "control-oracles" / f"{family}.md")
print("Copied unchanged S01/S05/S10 stimuli and independent oracles; no consumer prepared")
