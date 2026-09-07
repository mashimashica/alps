"""Apply the preregistered paired analysis to adjudicated observations.

Experiment-only calculation, not an ALPS evaluator or product record contract.
The schedule fixes denominators independently of received grades. This program
does not read Skill prose, infer adequacy, attribute defects or approve a release.
"""

import argparse
import csv
from collections import defaultdict
import hashlib
import math
from pathlib import Path
import random
from statistics import mean


VARIANTS = ("ordinary", "challenging")
LABELS = {"adequate": 1, "bounded deficiency": 0, "material failure": 0,
          "unconfirmed": None}


def read_tsv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_frozen_tsv(path, expected_sha256):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected_sha256:
        raise ValueError(f"Input differs from the prospectively frozen basis: {path}")
    return read_tsv(path)


def case_types(rows, cells):
    """Use predeclared whole-application case types, never infer them from grades."""
    result = {}
    expected = {(key[0], variant) for key in cells for variant in VARIANTS}
    for row in rows:
        key = row["case"], row["variant"]
        if key not in expected or key in result:
            raise ValueError("Unexpected or duplicate case-type mapping")
        if row["case_type"] not in {"positive", "incomplete", "failure"}:
            raise ValueError("Use the predeclared whole-application case type")
        result[key] = row["case_type"]
    if set(result) != expected:
        raise ValueError("Every scheduled family/variant needs its frozen case type")
    return result


def at_least(value, threshold):
    # Integer counts become rational weighted means; binary cancellation must
    # not reject an exact 5-point or 20-percent boundary. This is roundoff-scale
    # tolerance, not a changed practical margin or an interval-zero tolerance.
    return value >= threshold or math.isclose(value, threshold, rel_tol=0, abs_tol=1e-12)


def build_cells(schedule, observations):
    """Reject malformed/unequal A/B schedules; preserve every planned case."""
    identities, slots, assignments = set(), {}, {}
    for row in schedule:
        trial = row["trial_id"]
        if trial in identities:
            raise ValueError(f"Duplicate scheduled trial: {trial}")
        identities.add(trial)
        if row["arm"] not in {"A", "B", "C"}:
            raise ValueError("Unexpected comparison arm")
        if row["arm"] == "C":
            continue  # C is a separately reported descriptive comparison.
        key = (row["case"], row["model"] + "/" + row["effort"], row["repetition"])
        if (key, row["arm"]) in assignments:
            raise ValueError("Duplicate paired schedule cell")
        assignments[key, row["arm"]] = trial
        for variant in VARIANTS:
            slots[trial, variant] = None
    if not slots:
        raise ValueError("No A/B slots in schedule")
    observed = set()
    for row in observations:
        key = row["trial_id"], row["variant"]
        if key not in slots:
            raise ValueError(f"Observation outside planned A/B slots: {key}")
        if key in observed:
            raise ValueError(f"Multiple observations for a slot: {key}; adjudicate attempts first")
        observed.add(key)
        if row["adequacy"] not in LABELS:
            raise ValueError("Use an adjudicated assessment label")
        adequacy = LABELS[row["adequacy"]]
        raw_count = row["compensations"]
        if raw_count and (not raw_count.isdecimal()):
            raise ValueError("Compensations must be a nonnegative integer or blank")
        count = int(raw_count) if raw_count else None
        if (adequacy is not None or count is not None) and not row["evidence"].strip():
            raise ValueError("Observed judgments need an evidence reference")
        if adequacy is None and count is not None:
            raise ValueError("Unconfirmed task observation cannot establish complete compensation count")
        slots[key] = (adequacy, count)
    cells, layout = {}, defaultdict(lambda: defaultdict(set))
    for key, arm in assignments:
        if arm != "A":
            if (key, "A") not in assignments:
                raise ValueError("Missing A pairing")
            continue
        if (key, "B") not in assignments:
            raise ValueError("Missing B pairing")
        family, configuration, repetition = key
        layout[family][configuration].add(repetition)
        cells[key] = {
            group: [slots[assignments[key, group], variant] or (None, None)
                    for variant in VARIANTS] for group in ("A", "B")}
    first = next(iter(layout.values()))
    shape = {config: set(reps) for config, reps in first.items()}
    if any({c: set(r) for c, r in configs.items()} != shape for configs in layout.values()):
        raise ValueError("Families must retain the same fixed configuration/repetition mixture")
    if len({len(reps) for reps in shape.values()}) != 1:
        raise ValueError("Configurations must have equally weighted repetitions")
    return cells, dict(layout)


def percentile(values, probability):
    """Linear percentile, retaining negative-infinity burden replicates."""
    values = sorted(values)
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    fraction = position - lower
    if fraction == 0 or lower == len(values) - 1:
        return values[lower]
    left, right = values[lower:lower + 2]
    if left == right or math.isinf(left):
        return left
    return left + fraction * (right - left)


def reduction(a, b):
    return 1 - b / a if a else (0.0 if not b else -math.inf)


def summarize(cells, keys, missing, burden):
    averages = {}
    counts = {}
    for arm in ("A", "B"):
        values = [value for key in keys for value, _ in cells[key][arm]]
        replacement = int((arm == "A") == (missing == "conservative"))
        averages[arm] = mean(replacement if v is None else v for v in values)
        if burden:
            counts[arm] = mean(count for key in keys for _, count in cells[key][arm])
    return (averages["A"], averages["B"], averages["B"] - averages["A"],
            reduction(counts["A"], counts["B"]) if burden else None,
            counts.get("A"), counts.get("B"))


def bootstrap_keys(layout, rng):
    families = sorted(layout)
    result = []
    for family in rng.choices(families, k=len(families)):
        for configuration in sorted(layout[family]):
            repetitions = sorted(layout[family][configuration])
            for repetition in rng.choices(repetitions, k=len(repetitions)):
                result.append((family, configuration, repetition))
    return result


def observation_counts(cells, keys):
    return {arm: {"planned": sum(len(cells[key][arm]) for key in keys),
                  "unconfirmed": sum(v is None for key in keys for v, _ in cells[key][arm])}
            for arm in ("A", "B")}


def analyze(cells, layout, replicates=10000, seed=700, types=None):
    if replicates < 1:
        raise ValueError("At least one bootstrap replicate is needed")
    keys = sorted(cells)
    missing_count = sum(value is None for cell in cells.values()
                        for arm in ("A", "B") for value, _ in cell[arm])
    burden = all(count is not None for cell in cells.values()
                 for arm in ("A", "B") for _, count in cell[arm])
    result = {"slots": len(keys) * 4, "unconfirmed": missing_count,
              "families": len(layout), "replicates": replicates, "seed": seed,
              "burden_observed": burden, "assignments": {}, "by_family": {},
              "by_configuration": {}, "by_variant": {}, "by_case_type": {},
              "leave_one_family_out": {}, "group_counts": {}}
    for assignment in (("conservative", "favorable") if missing_count else ("observed",)):
        point = summarize(cells, keys, assignment, burden)
        rng = random.Random(seed)
        draws = [summarize(cells, bootstrap_keys(layout, rng), assignment, burden)
                 for _ in range(replicates)]
        interval = [percentile([d[2] for d in draws], q) for q in (.025, .975)]
        burden_interval = ([percentile([d[3] for d in draws], q) for q in (.025, .975)]
                           if burden and point[4] > 0 else None)
        result["assignments"][assignment] = {
            "point": point, "adequacy_interval": interval,
            "burden_interval": burden_interval,
            "effectiveness_numeric_gate": at_least(point[2], .05) and interval[0] > 0,
            "burden_numeric_gate": bool(burden_interval is not None
                                        and interval[0] > -.05
                                        and at_least(point[3], .20) and burden_interval[0] > 0)}
    # Descriptive bounds retain every slot; no subgroup gate or extra inference.
    for output_key, key_index in (("by_family", 0), ("by_configuration", 1)):
        for label in sorted({key[key_index] for key in keys}):
            subset = [key for key in keys if key[key_index] == label]
            result[output_key][label] = [summarize(cells, subset, a, False)[:3]
                                        for a in ("conservative", "favorable")]
            result["group_counts"][output_key, label] = observation_counts(cells, subset)
    for index, variant in enumerate(VARIANTS):
        variant_cells = {key: {arm: [cell[arm][index]] for arm in ("A", "B")}
                         for key, cell in cells.items()}
        result["by_variant"][variant] = [summarize(variant_cells, keys, a, False)[:3]
                                         for a in ("conservative", "favorable")]
        result["group_counts"]["by_variant", variant] = observation_counts(variant_cells, keys)
    if types is not None:
        for label in sorted(set(types.values())):
            subset = {}
            for key, cell in cells.items():
                indices = [i for i, variant in enumerate(VARIANTS) if types[key[0], variant] == label]
                if indices:
                    subset[key] = {arm: [cell[arm][i] for i in indices] for arm in ("A", "B")}
            result["by_case_type"][label] = [summarize(subset, sorted(subset), a, False)[:3]
                                             for a in ("conservative", "favorable")]
            result["group_counts"]["by_case_type", label] = observation_counts(subset, sorted(subset))
    if len(layout) > 1:
        for excluded in sorted(layout):
            subset = [key for key in keys if key[0] != excluded]
            result["leave_one_family_out"][excluded] = [summarize(cells, subset, a, False)[:3]
                                                        for a in ("conservative", "favorable")]
            result["group_counts"]["leave_one_family_out", excluded] = observation_counts(cells, subset)
    return result


def render(result):
    def percent(value):
        return f"{100 * value:.2f}%"

    print("# Paired A/B calculation\n")
    print(f"Planned applications: {result['slots']}; unconfirmed: {result['unconfirmed']}. "
          f"Family clusters: {result['families']}. Bootstrap: {result['replicates']} replicates, "
          f"analysis seed {result['seed']}.\n")
    print("| Assignment | A adequacy | B adequacy | B − A | 95% interval | Effectiveness numeric gate |")
    print("| --- | ---: | ---: | ---: | --- | --- |")
    for label, data in result["assignments"].items():
        point, interval = data["point"], data["adequacy_interval"]
        print(f"| {label} | {percent(point[0])} | {percent(point[1])} | {percent(point[2])} | "
              f"{percent(interval[0])} to {percent(interval[1])} | {data['effectiveness_numeric_gate']} |")
    print("\nNumeric gates alone do not accept a candidate. Semantic, attribution, material-regression, "
          "distribution and final-package gates require their separate evidence. "
          "Unconfirmed observations are bounded, not removed; divergent assignment gates remain unconfirmed.\n")
    for label, data in result["assignments"].items():
        interval = data["burden_interval"]
        if interval is None:
            print(f"Burden route ({label}): unavailable (unknown counts or zero observed A mean).\n")
        else:
            point = data["point"]
            print(f"Burden ({label}): A mean {point[4]:.4f}, B mean {point[5]:.4f}; "
                  f"reduction {percent(point[3])}, 95% interval {percent(interval[0])} to "
                  f"{percent(interval[1])}; numeric gate {data['burden_numeric_gate']}.\n")
    for section in ("by_family", "by_configuration", "by_variant", "by_case_type", "leave_one_family_out"):
        print(f"## {section.replace('_', ' ')}\n")
        print("| Group | Planned A / B | Unconfirmed A / B | Conservative A / B / difference | Favorable A / B / difference |")
        print("| --- | ---: | ---: | --- | --- |")
        for label, bounds in result[section].items():
            counts = result["group_counts"][section, label]
            print(f"| {label} | {counts['A']['planned']} / {counts['B']['planned']} | "
                  f"{counts['A']['unconfirmed']} / {counts['B']['unconfirmed']} | "
                  f"{' / '.join(map(percent, bounds[0]))} | "
                  f"{' / '.join(map(percent, bounds[1]))} |")
        print()
    print("These are empirical synthetic-case estimates. The family sample and fixed model mixture "
          "do not establish representativeness of other business work. Business Outcome achievement, "
          "artifact quality, C-arm results and causal explanations are reported separately.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schedule", help="Immutable creator schedule TSV (not the mutable execution ledger)")
    parser.add_argument("observations", help="Adjudicated A/B TSV: trial_id, variant, adequacy, compensations, evidence")
    parser.add_argument("case_types", help="Prospective TSV: case, variant, case_type (positive/incomplete/failure)")
    parser.add_argument("--schedule-sha256", required=True, help="Digest from the verified pre-execution checkpoint")
    parser.add_argument("--case-types-sha256", required=True, help="Digest from the verified pre-evaluation checkpoint")
    args = parser.parse_args()
    cells, layout = build_cells(read_frozen_tsv(args.schedule, args.schedule_sha256), read_tsv(args.observations))
    types = case_types(read_frozen_tsv(args.case_types, args.case_types_sha256), cells)
    render(analyze(cells, layout, types=types))


if __name__ == "__main__":
    main()
