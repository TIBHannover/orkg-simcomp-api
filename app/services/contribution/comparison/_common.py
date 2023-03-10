# -*- coding: utf-8 -*-
from typing import List, Optional

from app.models.contribution import ComparisonHeaderCell
from app.services.common.orkg_backend import OrkgBackendWrapperService


def get_contribution_details(
    orkg_backend: OrkgBackendWrapperService,
    contribution_id: str,
) -> Optional[ComparisonHeaderCell]:
    # TODO: this call should be replaced by another optimized one from the backend.
    contribution_details = orkg_backend.get_contribution_details(contribution_id)

    if not contribution_details:
        return None

    return ComparisonHeaderCell(
        id=contribution_id,
        label=contribution_details["label"],
        paper_id=contribution_details["paper_id"],
        paper_label=contribution_details["paper_label"],
        paper_year=orkg_backend.get_paper_year(contribution_details["paper_id"]),
    )


def clean_classes(
    classes: List[str],
) -> List[str]:
    return [
        c
        for c in classes
        if c
        not in [
            "Thing",
            "Literal",
            "AuditableEntity",  # TODO: remove this when it is removed from the graph
            "Resource",
        ]
    ]
