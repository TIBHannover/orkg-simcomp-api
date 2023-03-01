# -*- coding: utf-8 -*-
import http
from typing import Union

import pandas as pd
from pydantic import ValidationError

from app.common.errors import OrkgSimCompApiError
from app.models.contribution import Comparison
from app.models.thing import ExportFormat


class ComparisonExporter:
    @staticmethod
    def export(
        comparison: Union[dict, Comparison],
        format: ExportFormat,
    ):
        comparison = ComparisonExporter._parse(comparison)

        try:
            return {
                format.CSV: ComparisonExporter._export_csv,
                format.DATAFRAME: ComparisonExporter._export_df,
            }[format](comparison)
        except KeyError:
            raise OrkgSimCompApiError(
                message='Exporting a comparison with the format="{}" is not supported'.format(
                    format
                ),
                cls=ComparisonExporter,
                status_code=http.HTTPStatus.NOT_IMPLEMENTED,
            )

    @staticmethod
    def _export_csv(comparison: Comparison):
        return ComparisonExporter._export_df(comparison).to_csv(index=True)

    @staticmethod
    def _export_df(
        comparison: Comparison,
    ) -> pd.DataFrame:
        columns = [
            "{}/{}".format(
                contribution.paper_label,
                contribution.label,
            )
            for contribution in comparison.contributions
        ]

        predicates_lookup = {predicate.id: predicate.label for predicate in comparison.predicates}

        indices = []
        rows = []
        for (
            predicate_id,
            contributions_targets,
        ) in comparison.data.items():
            indices.append(predicates_lookup[predicate_id])

            row = []
            for targets in contributions_targets:
                if not targets[0]:
                    row.append("")
                    continue

                target_cell = [target.label for target in targets]
                row.append("<SEP>".join(target_cell))

            rows.append(row)

        return pd.DataFrame(rows, columns=columns, index=indices)

    @staticmethod
    def _parse(comparison: Union[dict, Comparison]) -> Comparison:
        if isinstance(comparison, Comparison):
            return comparison

        try:
            return Comparison(
                contributions=comparison["contributions"],
                predicates=comparison["predicates"],
                data=comparison["data"],
            )
        except (KeyError, ValidationError):
            raise OrkgSimCompApiError(
                message="Data object cannot be parsed as a Comparison",
                cls=ComparisonExporter,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            )
