"""
test_project_structure.py
Validates project directories, config JSON schema integrity, and initial dependencies.
"""

import json
import os
import unittest
from pathlib import Path


class TestProjectStructure(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent

    def test_required_directories_exist(self):
        required_dirs = [
            "config",
            "data/synthetic",
            "data/workloads",
            "results/raw",
            "results/processed",
            "results/figures",
            "reports",
            "src/data_generator",
            "src/simulation",
            "src/security",
            "src/experiments",
            "src/visualization",
            "tests",
        ]
        for d in required_dirs:
            target_path = self.root_dir / d
            self.assertTrue(target_path.is_dir(), f"Expected directory missing: {d}")

    def test_simulation_config_valid(self):
        config_path = self.root_dir / "config" / "simulation_config.json"
        self.assertTrue(config_path.is_file(), "simulation_config.json missing")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("simulation", data)
        self.assertIn("on_premise", data)
        self.assertIn("hybrid_cloud", data)
        self.assertIn("private_tier", data["hybrid_cloud"])
        self.assertIn("public_tier", data["hybrid_cloud"])

    def test_workloads_config_valid(self):
        config_path = self.root_dir / "config" / "workloads_config.json"
        self.assertTrue(config_path.is_file(), "workloads_config.json missing")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("workloads", data)
        for w in ["W1", "W2", "W3", "W4", "W5", "W6"]:
            self.assertIn(w, data["workloads"], f"Workload {w} missing from config")

    def test_security_rules_valid(self):
        config_path = self.root_dir / "config" / "security_rules.json"
        self.assertTrue(config_path.is_file(), "security_rules.json missing")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("classification_levels", data)
        self.assertIn("service_classification_mapping", data)
        for lvl in ["RESTRICTED", "CONFIDENTIAL", "INTERNAL", "PUBLIC"]:
            self.assertIn(lvl, data["classification_levels"])


if __name__ == "__main__":
    unittest.main()
