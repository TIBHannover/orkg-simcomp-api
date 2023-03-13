# -*- coding: utf-8 -*-
import http
from typing import Any, Dict, List, Union

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
        config: Dict[str, Any] = None,
        thing_service: ... = None,
        like_ui: bool = False,
        **kwargs
    ):
        comparison = ComparisonExporter._parse(comparison)

        try:
            return {
                format.HTML: ComparisonExporter._export_html,
                format.CSV: ComparisonExporter._export_csv,
                format.DATAFRAME: ComparisonExporter._export_df,
            }[format](comparison, config, like_ui)
        except KeyError:
            raise OrkgSimCompApiError(
                message='Exporting a comparison with the format="{}" is not supported'.format(
                    format
                ),
                cls=ComparisonExporter,
                status_code=http.HTTPStatus.NOT_IMPLEMENTED,
            )

    @staticmethod
    def _export_html(comparison: Comparison, config: Dict[str, Any], like_ui: bool):
        return ComparisonExporter._export_df(comparison, config, like_ui).to_html()

    @staticmethod
    def _export_csv(comparison: Comparison, config: Dict[str, Any], like_ui: bool):
        return ComparisonExporter._export_df(comparison, config, like_ui).to_csv(index=True)

    @staticmethod
    def _export_df(comparison: Comparison, config: Dict[str, Any], like_ui: bool) -> pd.DataFrame:
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

        df = pd.DataFrame(rows, columns=columns, index=indices)

        if like_ui:
            ui_predicates = ComparisonExporter._parse_config(config)

            if ui_predicates:
                # remove props that are not displayed
                df = df.drop(
                    [
                        p_lbl
                        for p_id, p_lbl in predicates_lookup.items()
                        if p_id not in ui_predicates
                    ]
                )
                # order df rows by ui props order
                df = df.reindex(
                    [predicates_lookup[p] for p in ui_predicates if p in predicates_lookup]
                )

        return df

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

    @staticmethod
    def _parse_config(config: Dict[str, Any]) -> List[str]:
        return config.get("predicates", [])
