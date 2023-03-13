# -*- coding: utf-8 -*-
from io import StringIO
from unittest import TestCase

import pandas as pd

from app.common.errors import OrkgSimCompApiError
from app.models.thing import ExportFormat
from app.services.thing.export import ComparisonExporter


class ComparisonExporterTest(TestCase):
    def setUp(self):
        self.config = {"predicates": ["predicate 1"]}
        self.comparison = {
            "contributions": [
                {
                    "id": "0",
                    "label": "Contribution 1",
                    "paper_id": "0",
                    "paper_label": "Paper 1",
                    "paper_year": "2023",
                },
                {
                    "id": "1",
                    "label": "Contribution 2",
                    "paper_id": "1",
                    "paper_label": "Paper 2",
                    "paper_year": "2023",
                },
            ],
            "predicates": [
                {
                    "id": "predicate 1",
                    "label": "predicate 1",
                    "n_contributions": 2,
                    "active": True,
                },
                {
                    "id": "predicate 2",
                    "label": "predicate 2",
                    "n_contributions": 2,
                    "active": True,
                },
            ],
            "data": {
                "predicate 1": [
                    [
                        {
                            "id": "predicate 1",
                            "label": "target 1",
                            "type": "literal",
                            "classes": [],
                            "path": [],
                            "path_labels": [],
                        }
                    ],
                    [
                        {
                            "id": "predicate 1",
                            "label": "target 1",
                            "type": "literal",
                            "classes": [],
                            "path": [],
                            "path_labels": [],
                        },
                        {
                            "id": "predicate 1",
                            "label": "target 2",
                            "type": "literal",
                            "classes": [],
                            "path": [],
                            "path_labels": [],
                        },
                    ],
                ],
                "predicate 2": [
                    [
                        {
                            "id": "predicate 2",
                            "label": "target 1",
                            "type": "literal",
                            "classes": [],
                            "path": [],
                            "path_labels": [],
                        }
                    ],
                    [
                        {
                            "id": "predicate 2",
                            "label": "target 1",
                            "type": "literal",
                            "classes": [],
                            "path": [],
                            "path_labels": [],
                        },
                        {
                            "id": "predicate 2",
                            "label": "target 2",
                            "type": "literal",
                            "classes": [],
                            "path": [],
                            "path_labels": [],
                        },
                    ],
                ],
            },
        }

    def test_export_raises_error_for_unknown_format(
        self,
    ):
        self.assertRaises(
            OrkgSimCompApiError,
            ComparisonExporter.export,
            self.comparison,
            ExportFormat.UNKNOWN,
        )

    def test_export_raises_error_for_unparsable_comparison(
        self,
    ):
        self.assertRaises(
            OrkgSimCompApiError,
            ComparisonExporter.export,
            {},
            ExportFormat.DATAFRAME,
        )

    def test_export_succeeds_df(self):
        df = ComparisonExporter.export(
            self.comparison,
            ExportFormat.DATAFRAME,
        )
        self._assert_df(df)

    def test_export_succeeds_like_ui_df(self):
        df = ComparisonExporter.export(
            self.comparison, ExportFormat.DATAFRAME, config=self.config, like_ui=True
        )
        self._assert_df(df, like_ui=True)

    def test_export_succeeds_csv(self):
        csv = ComparisonExporter.export(self.comparison, ExportFormat.CSV)
        df = pd.read_csv(StringIO(csv), index_col=0)
        self._assert_df(df)

    def test_export_succeeds_like_ui_csv(self):
        csv = ComparisonExporter.export(
            self.comparison, ExportFormat.CSV, config=self.config, like_ui=True
        )
        df = pd.read_csv(StringIO(csv), index_col=0)
        self._assert_df(df, like_ui=True)

    def _assert_df(self, df, like_ui=False):
        # checking header
        for i, column in enumerate(df.columns.to_list()):
            expected_header = "{}/{}".format(
                self.comparison["contributions"][i]["paper_label"],
                self.comparison["contributions"][i]["label"],
            )
            self.assertEqual(column, expected_header)

        # checking index
        if like_ui:
            self.assertEqual(
                len(df.index.values),
                len(self.config["predicates"]),
            )

            self.assertEqual(
                df.index.values.tolist(),
                [predicate for predicate in self.config["predicates"]],
            )
        else:
            self.assertEqual(
                len(df.index.values),
                len(self.comparison["predicates"]),
            )

            self.assertEqual(
                df.index.values.tolist(),
                [predicate["label"] for predicate in self.comparison["predicates"]],
            )

        # checking targets
        for row_i, row in df.iterrows():
            for column_i, column in enumerate(df.columns.to_list()):
                targets = [target["label"] for target in self.comparison["data"][row_i][column_i]]
                expected_target = "<SEP>".join(targets)
                self.assertEqual(
                    df[column][row_i],
                    expected_target,
                )
