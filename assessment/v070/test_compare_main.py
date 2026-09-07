"""Numerical/denominator checks for the experiment calculation, not Skill prose."""

from collections import Counter
import hashlib
import math
from pathlib import Path
import random
import tempfile
import unittest

from compare_main import (analyze, at_least, bootstrap_keys, build_cells, case_types,
                          percentile, read_frozen_tsv, reduction)


def fixture(families=3, configurations=2, repetitions=2, a=0, b=1, ac=2, bc=1):
    schedule, grades = [], []
    for family in range(families):
        for config in range(configurations):
            for repeat in range(repetitions):
                for arm, value, count in (("A", a, ac), ("B", b, bc)):
                    trial = f"{family}-{config}-{repeat}-{arm}"
                    schedule.append(dict(trial_id=trial, case=str(family), model=str(config),
                                         effort="fixed", repetition=str(repeat), arm=arm))
                    for variant in ("ordinary", "challenging"):
                        grades.append(dict(trial_id=trial, variant=variant,
                                           adequacy="adequate" if value else "material failure",
                                           compensations=str(count), evidence="synthetic fixture"))
    return schedule, grades


class ComparisonChecks(unittest.TestCase):
    def test_exact_practical_boundaries_are_not_rejected_by_binary_roundoff(self):
        schedule, grades = fixture(a=1, b=1, ac=5, bc=4)
        measured = analyze(*build_cells(schedule, grades), replicates=100)["assignments"]["observed"]
        self.assertTrue(measured["burden_numeric_gate"])
        self.assertTrue(at_least(1 - .95, .05))
        self.assertTrue(at_least(.3 - .25, .05))
        self.assertFalse(at_least(.049999999, .05))
        self.assertFalse(at_least(.199999999, .20))

    def test_symmetric_schedule_deletion_fails_frozen_identity_check(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "schedule.tsv"
            path.write_text("trial_id\tarm\nfirst\tA\nsecond\tB\n")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(len(read_frozen_tsv(path, digest)), 2)
            path.write_text("trial_id\tarm\n")
            with self.assertRaises(ValueError):
                read_frozen_tsv(path, digest)

    def test_case_type_map_is_complete_independent_and_used_for_subgroups(self):
        cells, layout = build_cells(*fixture(families=2, configurations=1))
        rows = [dict(case=family, variant=variant, case_type=label)
                for family in ("0", "1")
                for variant, label in (("ordinary", "positive"), ("challenging", "incomplete"))]
        types = case_types(rows, cells)
        result = analyze(cells, layout, replicates=100, types=types)
        self.assertEqual(set(result["by_case_type"]), {"positive", "incomplete"})
        self.assertEqual(result["by_case_type"]["incomplete"][0], (0, 1, 1))
        with self.assertRaises(ValueError):
            case_types(rows[:-1], cells)
        with self.assertRaises(ValueError):
            case_types(rows + [rows[0]], cells)

    def test_known_constant_difference_and_clustered_draws(self):
        schedule, grades = fixture()
        cells, layout = build_cells(schedule, grades)
        result = analyze(cells, layout, replicates=200)
        measured = result["assignments"]["observed"]
        self.assertEqual(result["slots"], 48)
        self.assertEqual(result["unconfirmed"], 0)
        self.assertEqual(measured["point"], (0, 1, 1, .5, 2, 1))
        self.assertEqual(measured["adequacy_interval"], [1, 1])
        self.assertEqual(measured["burden_interval"], [.5, .5])
        self.assertTrue(measured["effectiveness_numeric_gate"])
        self.assertTrue(measured["burden_numeric_gate"])
        self.assertEqual(len(result["leave_one_family_out"]), 3)

    def test_missing_slots_remain_in_denominator_and_reverse_gates(self):
        schedule, _ = fixture(families=2, configurations=1)
        cells, layout = build_cells(schedule, [])
        result = analyze(cells, layout, replicates=100)
        self.assertEqual(result["slots"], 16)
        self.assertEqual(result["unconfirmed"], 16)
        self.assertFalse(result["burden_observed"])
        conservative = result["assignments"]["conservative"]
        favorable = result["assignments"]["favorable"]
        self.assertEqual(conservative["point"][:3], (1, 0, -1))
        self.assertEqual(favorable["point"][:3], (0, 1, 1))
        self.assertFalse(conservative["effectiveness_numeric_gate"])
        self.assertTrue(favorable["effectiveness_numeric_gate"])
        self.assertIsNone(conservative["burden_interval"])

    def test_one_missing_observation_does_not_remove_its_pair(self):
        schedule, grades = fixture(families=1, configurations=1, repetitions=1)
        grades.pop()
        result = analyze(*build_cells(schedule, grades), replicates=100)
        self.assertEqual(result["slots"], 4)
        self.assertEqual(result["unconfirmed"], 1)
        self.assertEqual(result["assignments"]["conservative"]["point"][:3], (0, .5, .5))
        self.assertEqual(result["assignments"]["favorable"]["point"][:3], (0, 1, 1))

    def test_unknown_compensation_disables_burden_only(self):
        schedule, grades = fixture()
        grades[0]["compensations"] = ""
        result = analyze(*build_cells(schedule, grades), replicates=100)
        measured = result["assignments"]["observed"]
        self.assertTrue(measured["effectiveness_numeric_gate"])
        self.assertFalse(measured["burden_numeric_gate"])
        self.assertIsNone(measured["burden_interval"])

    def test_zero_baseline_burden_is_unavailable_and_draws_retained(self):
        schedule, grades = fixture(a=1, b=1, ac=0, bc=0)
        result = analyze(*build_cells(schedule, grades), replicates=100)
        self.assertIsNone(result["assignments"]["observed"]["burden_interval"])
        self.assertEqual(reduction(0, 0), 0)
        self.assertEqual(reduction(0, 1), -math.inf)
        self.assertEqual(percentile([-math.inf, 0, 1], .025), -math.inf)
        self.assertEqual(percentile([-math.inf, -math.inf, 1], .025), -math.inf)
        self.assertEqual(percentile([0, 1, 2, 3, 4], .025), .1)

    def test_duplicate_and_outside_observations_are_not_best_of_attempts(self):
        schedule, grades = fixture()
        with self.assertRaises(ValueError):
            build_cells(schedule, grades + [dict(grades[0])])
        grades[0]["trial_id"] = "not planned"
        with self.assertRaises(ValueError):
            build_cells(schedule, grades)

    def test_unbalanced_schedule_rejected(self):
        schedule, grades = fixture()
        with self.assertRaises(ValueError):
            build_cells(schedule[:-1], [])
        with self.assertRaises(ValueError):
            build_cells(schedule + [dict(schedule[0])], [])
        # Remove an entire paired repetition from only one family/configuration.
        with self.assertRaises(ValueError):
            build_cells(schedule[2:], [])

    def test_observations_need_evidence_and_valid_counts(self):
        schedule, grades = fixture()
        for field, value in (("evidence", ""), ("compensations", "-1"),
                             ("compensations", "0.5"), ("adequacy", "guessed")):
            changed = [dict(row) for row in grades]
            changed[0][field] = value
            with self.assertRaises(ValueError):
                build_cells(schedule, changed)

    def test_bootstrap_retains_configuration_mixture_and_pair_units(self):
        cells, layout = build_cells(*fixture(families=4, configurations=3))
        keys = bootstrap_keys(layout, random.Random(700))
        self.assertEqual(len(keys), 24)
        self.assertEqual(Counter(key[1] for key in keys),
                         {"0/fixed": 8, "1/fixed": 8, "2/fixed": 8})
        self.assertTrue(all(key in cells and set(cells[key]) == {"A", "B"} for key in keys))
        self.assertEqual(keys, bootstrap_keys(layout, random.Random(700)))

    def test_equal_configuration_weights_and_separate_case_types(self):
        schedule, grades = fixture(families=2, configurations=2, a=1, b=1)
        for row in grades:
            _, config, _, arm = row["trial_id"].split("-")
            if arm == "B" and config == "0" and row["variant"] == "challenging":
                row["adequacy"] = "material failure"
        result = analyze(*build_cells(schedule, grades), replicates=100)
        self.assertEqual(result["assignments"]["observed"]["point"][:3], (1, .75, -.25))
        self.assertEqual(result["by_variant"]["ordinary"][0], (1, 1, 0))
        self.assertEqual(result["by_variant"]["challenging"][0], (1, .5, -.5))


if __name__ == "__main__":
    unittest.main()
