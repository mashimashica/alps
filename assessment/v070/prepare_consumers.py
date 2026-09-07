"""Copy completed generated Skills into separate fresh-consumer task folders.

The coordinator explicitly selects completed creators. This helper never infers
quality or completion from file existence and never copies grading oracles.
"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from booking_state import prepare as prepare_booking

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("creator_ids", nargs="+")
    args = parser.parse_args()
    for creator_id in args.creator_ids:
        creator = ROOT / "trials" / creator_id
        assignment = json.loads((creator / "assignment.json").read_text())
        development = creator_id.startswith(("dev1-", "dev2-"))
        if development and assignment["case"] not in {"S05", "S08", "S10"}:
            raise SystemExit("No reviewed development consumer case for this family")
        skills = [p for p in (creator / "output").iterdir() if p.is_dir() and (p / "SKILL.md").is_file()]
        if len(skills) != 1:
            raise SystemExit(f"Expected one completed target Skill: {creator_id}")
        number = int(creator_id.rsplit("-", 1)[1])
        for index, variant in enumerate(("ordinary", "challenging")):
            prefix = "D" + creator_id.split("-")[0][-1] + "-U" if development else "U"
            use_id = f"{prefix}{2 * (number - 1) + index + 1:03}"
            folder = ROOT / "consumers" / use_id
            folder.mkdir(parents=True, exist_ok=False)
            (folder / "work").mkdir()
            shutil.copytree(skills[0], folder / "skill" / skills[0].name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            source = ROOT / ("development-consumer-cases" if development else "consumer-source") / assignment["case"] / variant
            if development and (source / "input").is_dir():
                source = source / "input"
            if development and assignment["case"] == "S08":
                prepare_booking(folder, source)
            else:
                shutil.copytree(source, folder / "input")
            if development and assignment["case"] != "S08":
                if assignment["case"] == "S10":
                    shutil.copy2(ROOT / "cases/S10/release_tool.py", folder / "input/release_tool.py")
                request = folder / "input/request.md"
                body = request.read_text(encoding="utf-8")
                replacements = {"{{INPUT_DIR}}": str(folder / "input"),
                                "{{ENVIRONMENT_PATH}}": str(folder / "input"),
                                "{{STATE_PATH}}": str(folder / "input/state.json")}
                for token, value in replacements.items():
                    body = body.replace(token, value)
                if "{{" in body:
                    raise SystemExit(f"Unresolved request path token: {use_id}")
                request.write_text(body, encoding="utf-8")
            target = folder / "skill" / skills[0].name
            prompt = f"""Use the Skill at {target}/SKILL.md to complete the user's task in {folder}/input/request.md with any accompanying files in that input folder. Write the user-facing answer to {folder}/answer.md using apply_patch. Use {folder}/work for temporary processing and permitted local outputs.

This is an application of the supplied Skill, not a request to redesign, repair, install or publish it. Do not modify the Skill. If it cannot support the requested work, report the concrete limitation and perform only independently valid work. Do not change external state or send messages. Synthetic state changes are allowed only when the task explicitly authorizes them, using its supplied interface; do not edit simulation state directly.

You may consult the frozen skill-creator aid at {ROOT}/frozen/skill-creator/SKILL.md if useful. It is available, not required. Read only your supplied Skill and its needed resources, your task input, that common authoring aid and any necessary standard runtime documentation. Do not read creator prompts, execution notes, sibling trials, evaluation plans, audits, expected answers or other worktrees. Do not delegate. The parent handles durable saving; do not commit, push, upload or install anything.

Record actual public commands, exit codes, relevant stdout/stderr and files used in {folder}/execution-note.md. Distinguish exact captured observations from summaries and unperformed checks; do not include private reasoning. If no tool is needed, say so. Your final response should give the answer and identify any limitation, not merely say that files were created.
"""
            (folder / "prompt.md").write_text(prompt, encoding="utf-8")
            copied = {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() for part in ("skill", "input") for p in (folder / part).rglob("*") if p.is_file()}
            metadata = {"consumer_id": use_id, "creator_id": creator_id, "case": assignment["case"], "variant": variant, "requested_model": "gpt-5.6-sol", "requested_effort": "high", "context": "fresh", "copied_sha256": copied, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
            (ROOT / "consumer-assignments").mkdir(exist_ok=True)
            (ROOT / "consumer-assignments" / f"{use_id}.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
            print(f"{use_id}: prepared from {creator_id}, {variant}; not started")


if __name__ == "__main__":
    main()
