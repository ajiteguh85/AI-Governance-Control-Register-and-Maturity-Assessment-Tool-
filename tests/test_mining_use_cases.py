"""Tests for mining industry AI-ML use case registry."""

import unittest

from ai_governance.mining_use_cases import (
    get_ai_adoption_best_practices,
    get_mining_use_case_catalogue,
    get_use_case_categories,
)
from ai_governance.validation import validate_use_case


class TestMiningUseCaseCatalogue(unittest.TestCase):
    def test_catalogue_not_empty(self):
        catalogue = get_mining_use_case_catalogue()
        self.assertGreater(len(catalogue), 5)

    def test_all_have_ids(self):
        for uc in get_mining_use_case_catalogue():
            self.assertTrue(uc.use_case_id.startswith("MN-UC-"))

    def test_all_have_techniques(self):
        for uc in get_mining_use_case_catalogue():
            self.assertGreater(len(uc.ai_techniques), 0)

    def test_all_have_data_sources(self):
        for uc in get_mining_use_case_catalogue():
            self.assertGreater(len(uc.data_sources), 0)

    def test_all_validate(self):
        for uc in get_mining_use_case_catalogue():
            result = validate_use_case(uc)
            self.assertTrue(result.is_valid, f"Use case {uc.use_case_id} failed validation")

    def test_unique_ids(self):
        catalogue = get_mining_use_case_catalogue()
        ids = [uc.use_case_id for uc in catalogue]
        self.assertEqual(len(ids), len(set(ids)))


class TestUseCaseCategories(unittest.TestCase):
    def test_categories_not_empty(self):
        cats = get_use_case_categories()
        self.assertGreater(len(cats), 8)

    def test_key_categories_present(self):
        cats = get_use_case_categories()
        for key in ["predictive_maintenance", "safety", "environmental_monitoring", "energy_management"]:
            self.assertIn(key, cats)


class TestBestPractices(unittest.TestCase):
    def test_categories_present(self):
        bp = get_ai_adoption_best_practices()
        self.assertIn("standards_and_policies", bp)
        self.assertIn("development_practices", bp)
        self.assertIn("monitoring_and_evaluation", bp)
        self.assertIn("innovation_and_improvement", bp)

    def test_each_has_items(self):
        for category, items in get_ai_adoption_best_practices().items():
            self.assertGreater(len(items), 0, f"Category '{category}' is empty")
            for item in items:
                self.assertIn("id", item)
                self.assertIn("title", item)
                self.assertIn("description", item)


if __name__ == "__main__":
    unittest.main()
