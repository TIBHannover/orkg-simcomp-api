# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import Mock

import networkx as nx
from parameterized import parameterized

from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.contribution.comparison import compare_merge
from tests.services.contribution.comparison.utils import create_subgraph


class TestCompareMerge(TestCase):
    def setUp(self):
        details = {
            "label": "Contribution 1",
            "paper_id": "paper_0",
            "paper_label": "Paper 1",
        }
        self.year = "2023"

        self.contributions = {
            "contribution_0": {
                "details": details,
                "subgraph": nx.DiGraph(),
            },
            "contribution_1": {
                "details": details,
                "subgraph": nx.DiGraph(),
            },
            "contribution_without_details": {
                "details": {},
                "subgraph": nx.DiGraph(),
            },
        }

        self.orkg_backend = OrkgBackendWrapperService()
        self.orkg_backend.get_contribution_details = Mock(
            side_effect=lambda x: self.contributions[x]["details"]
        )
        self.orkg_backend.get_paper_year = Mock(return_value=self.year)
        self.orkg_backend.get_subgraph = Mock(
            side_effect=lambda thing_id: self.contributions[thing_id]["subgraph"]
        )

    def test_compare_succeeds_with_empty_list(
        self,
    ):
        comparison = compare_merge.compare(self.orkg_backend, [])
        self.assertEqual(comparison.contributions, [])
        self.assertEqual(comparison.predicates, [])
        self.assertEqual(comparison.data, {})

    @parameterized.expand(
        [
            (
                ["contribution_0"],
                [{"has_research_field": "science"}],
            ),
            (
                [
                    "contribution_0",
                    "contribution_without_details",
                ],
                [
                    {"has_research_field": "science"},
                    {"has_research_field": "science"},
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {},
                    {"has_research_field": "science"},
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [{}, {}],
            ),
            (
                [
                    "contribution_without_details",
                    "contribution_1",
                ],
                [
                    {},
                    {"has_research_field": "science"},
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {"has_research_field": "science"},
                    {"has_research_field": "science"},
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {"has_research_field": "science"},
                    {
                        "has_research_field": "science",
                        "has_result": "0.12",
                    },
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {
                        "has_research_field": "science",
                        "has_result": "0.12",
                        "points_to": "hello",
                    },
                    {
                        "has_research_field": "science",
                        "has_result": "0.12",
                        "pointed_from": "hallo",
                    },
                ],
            ),
        ]
    )
    def test_compare_succeeds_with_simple_contributions(
        self, contribution_ids, contribution_dicts
    ):
        for i in range(len(contribution_ids)):
            self.contributions[contribution_ids[i]]["subgraph"] = create_subgraph(
                contribution_ids[i],
                contribution_dicts[i],
            )

        comparison = compare_merge.compare(self.orkg_backend, contribution_ids)
        self._assert_comparison(
            comparison,
            contribution_ids,
            contribution_dicts,
        )

    @parameterized.expand(
        [
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {"has_research_field": "science"},
                    {"research_field": "science"},
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {"use": "python"},
                    {"uses": "java"},
                ],
            ),
            (
                [
                    "contribution_0",
                    "contribution_1",
                ],
                [
                    {"employ": "nltk"},
                    {"emply": "scikit-learn"},
                ],
            ),
        ]
    )
    def test_compare_succeeds_and_merges_properties(self, contribution_ids, contribution_dicts):
        for i in range(len(contribution_ids)):
            self.contributions[contribution_ids[i]]["subgraph"] = create_subgraph(
                contribution_ids[i],
                contribution_dicts[i],
            )

        comparison = compare_merge.compare(self.orkg_backend, contribution_ids)
        self.assert_predicates_merged(
            comparison,
            contribution_dicts,
        )

    def _assert_comparison(
        self,
        comparison,
        contribution_ids,
        contribution_dicts,
    ):
        refined_ids = []
        refined_dicts = []

        for (
            contribution_id,
            contribution_dict,
        ) in zip(contribution_ids, contribution_dicts):
            if contribution_id != "contribution_without_details" and contribution_dict:
                refined_ids.append(contribution_id)
                refined_dicts.append(contribution_dict)

        contribution_ids = refined_ids
        contribution_dicts = refined_dicts

        # Checking contributions
        self.assertEqual(
            len(comparison.contributions),
            len(contribution_ids),
        )
        for i, contribution_id in enumerate(contribution_ids):
            self.assertEqual(
                comparison.contributions[i].id,
                contribution_id,
            )
            self.assertEqual(
                comparison.contributions[i].label,
                self.contributions[contribution_id]["details"]["label"],
            )

            self.assertEqual(
                comparison.contributions[i].paper_label,
                self.contributions[contribution_id]["details"]["paper_label"],
            )
            self.assertEqual(
                comparison.contributions[i].paper_id,
                self.contributions[contribution_id]["details"]["paper_id"],
            )

            self.assertEqual(
                comparison.contributions[i].paper_year,
                self.year,
            )

        # Checking predicates
        predicates = [
            key for contribution_dict in contribution_dicts for key in contribution_dict.keys()
        ]
        self.assertEqual(
            len(comparison.predicates),
            len(set(predicates)),
        )
        for predicate in comparison.predicates:
            self.assertTrue(predicate.id in predicates)
            self.assertTrue(predicate.label in predicates)
            self.assertEqual(
                predicate.n_contributions,
                predicates.count(predicate.id),
            )
            self.assertEqual(
                predicate.active,
                predicates.count(predicate.id) >= 2,
            )

        # Checking data
        self.assertEqual(
            len(comparison.data),
            len(set(predicates)),
        )
        for (
            predicate_id,
            contributions_data,
        ) in comparison.data.items():
            self.assertEqual(
                len(contributions_data),
                len(contribution_ids),
            )

            for (
                contribution_index,
                contribution_targets,
            ) in enumerate(contributions_data):
                for target in contribution_targets:
                    if target:
                        self.assertEqual(
                            target.id,
                            contribution_dicts[contribution_index][predicate_id],
                        )
                        self.assertEqual(
                            target.label,
                            contribution_dicts[contribution_index][predicate_id],
                        )
                        self.assertEqual(target.type, "literal")

    def assert_predicates_merged(
        self,
        comparison,
        contribution_dicts,
    ):
        self.assertEqual(
            len(comparison.data.keys()),
            1,
        )
        for predicate in comparison.predicates:
            self.assertTrue(predicate.id in contribution_dicts[0].keys())
            self.assertTrue(predicate.label in contribution_dicts[0].keys())
            self.assertEqual(
                predicate.n_contributions,
                len(contribution_dicts),
            )
            self.assertEqual(
                predicate.active,
                True,
            )
            self.assertNotEqual(
                predicate.similar_predicates,
                [],
            )
