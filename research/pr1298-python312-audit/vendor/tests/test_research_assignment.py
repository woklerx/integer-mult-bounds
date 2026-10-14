"""Task selection must be reproducible without promising exclusive ownership."""

import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("choose_research_task", ROOT / "scripts/choose_research_task.py")
assignment = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assignment)
CATALOG = json.loads((ROOT / assignment.CATALOG).read_text(encoding="utf-8"))


class ResearchAssignmentTests(unittest.TestCase):
    def test_catalog_sources_and_weights(self):
        assignment.validate_catalog(CATALOG, ROOT)

    def test_documented_allocation_matches_catalog(self):
        guide = (ROOT / "autoresearch.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| [^|\n]*\(`([a-z0-9-]+)`\) \| (\d+)% \|", guide, re.MULTILINE)
        self.assertEqual(len(rows), len(CATALOG["tracks"]))
        self.assertEqual(
            {ident: int(weight) for ident, weight in rows},
            {track["id"]: track["weight"] for track in CATALOG["tracks"]},
        )

    def test_reproducible_and_track_override(self):
        seed = "a1" * 16
        first = assignment.select(CATALOG, seed)
        self.assertEqual(first, assignment.select(CATALOG, seed.upper()))
        for track in CATALOG["tracks"]:
            result = assignment.select(CATALOG, seed, track["id"])
            self.assertEqual(result["track"], track["id"])
            self.assertEqual(len(result["suggestions"]), min(3, len(track["tasks"])))
            tasks = {t["id"]: t for t in track["tasks"]}
            for suggestion in result["suggestions"]:
                task = tasks[suggestion["task_id"]]
                self.assertIn(suggestion["method"], task["methods"])

    def test_nonce_does_not_make_same_scope_unique(self):
        seen = {}
        collision = False
        for nonce in range(40):
            result = assignment.select(CATALOG, f"{nonce:032x}", "complex-mechanisms")
            for card in result["suggestions"]:
                semantic = (card["task_id"], card["method"])
                if semantic in seen:
                    self.assertEqual(seen[semantic], card["scope_key"])
                    collision = True
                seen[semantic] = card["scope_key"]
        self.assertTrue(collision)

    def test_bad_seed_or_track_fails(self):
        for seed in ("", "1", "z" * 32, "0" * 33):
            with self.assertRaises(ValueError):
                assignment.select(CATALOG, seed)
        with self.assertRaises(ValueError):
            assignment.select(CATALOG, "0" * 32, "nonexistent")
        with self.assertRaises(ValueError):
            assignment.select(CATALOG, "0" * 32, "complex-mechanisms", "connector-alphabet-change")

    def test_specific_card_exposes_first_step_and_scope_changes(self):
        result = assignment.select(CATALOG, "0" * 32, task_id="connector-alphabet-change")
        self.assertEqual(len(result["suggestions"]), 1)
        card = result["suggestions"][0]
        self.assertIn("source count", card["scope_change_triggers"][0])
        self.assertIn("PASS_UNIVERSAL_CONNECTOR_BOUNDARY", card["first_step"]["expected"])
        self.assertTrue(card["first_experiment"])

    def test_broken_catalog_rejected(self):
        for mutation in ("weight", "duplicate", "missing-source", "empty-methods", "revision", "missing-log"):
            catalog = copy.deepcopy(CATALOG)
            track = catalog["tracks"][0]
            if mutation == "weight":
                track["weight"] += 1
            elif mutation == "duplicate":
                track["tasks"].append(copy.deepcopy(track["tasks"][0]))
            elif mutation == "missing-source":
                track["tasks"][0]["starting_points"] = ["does-not-exist"]
            elif mutation == "empty-methods":
                track["tasks"][0]["methods"] = []
            elif mutation == "revision":
                catalog["priority_revision"] = 0
            else:
                catalog["priority_log"] = "does-not-exist"
            with self.assertRaises(ValueError):
                assignment.validate_catalog(catalog, ROOT)

    def test_cli_dynamic_selected_record_and_receipt(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/choose_research_task.py"), "--seed", "0" * 32],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        receipt = json.loads(result.stdout)
        selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["selected"]["reproduce"], selected["reproduce"])
        self.assertEqual(receipt["selected"]["review"], selected["review"])
        self.assertEqual(receipt["status"], "SUGGESTIONS_ONLY_NOT_RESERVED")
        self.assertEqual(receipt["priority_revision"], CATALOG["priority_revision"])
        self.assertEqual(receipt["priority_log"], CATALOG["priority_log"])
        self.assertEqual(len(receipt["catalog_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
