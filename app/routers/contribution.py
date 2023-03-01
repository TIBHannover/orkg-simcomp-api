# -*- coding: utf-8 -*-
import http
from typing import List, Union

from fastapi import APIRouter, Depends, Query
from starlette.responses import StreamingResponse

from app.common.util.decorators import log
from app.models.common import Response
from app.models.contribution import (
    ComparisonType,
    ContributionComparisonResponse,
    ContributionSimilarityIndexResponse,
    ContributionSimilarityInitIndexResponse,
    ContributionSimilaritySimilarResponse,
)
from app.models.thing import ExportFormat
from app.services.common.es import ElasticsearchService
from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.common.wrapper import ResponseWrapper
from app.services.contribution import (
    ContributionComparisonService,
    ContributionSimilarityService,
)

router = APIRouter(prefix="/contribution", tags=["contribution"])


@router.post(
    "/internal/init",
    response_model=ContributionSimilarityInitIndexResponse,
    status_code=http.HTTPStatus.OK,
)
@log(__name__)
def initializes_es_index(
    orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
    es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance),
):
    service = ContributionSimilarityService(orkg_backend, es_service)
    return ResponseWrapper.wrap_json(service.init_index())


@router.post(
    "/internal/index",
    response_model=ContributionSimilarityIndexResponse,
    status_code=http.HTTPStatus.OK,
)
@log(__name__)
def indexes_a_contribution(
    contribution_id: str,
    orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
    es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance),
):
    service = ContributionSimilarityService(orkg_backend, es_service)
    return ResponseWrapper.wrap_json(service.index(contribution_id))


@router.get(
    "/similar",
    response_model=ContributionSimilaritySimilarResponse,
    status_code=http.HTTPStatus.OK,
)
@log(__name__)
def queries_similar_contributions(
    contribution_id: str,
    n_results: int = 10,
    orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
    es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance),
):
    service = ContributionSimilarityService(orkg_backend, es_service)
    return ResponseWrapper.wrap_json(service.query(contribution_id, n_results))


@router.get(
    "/compare",
    response_model=Union[ContributionComparisonResponse, Response],
    status_code=http.HTTPStatus.OK,
)
@log(__name__)
def compares_contributions(
    contributions: List[str] = Query(None),
    type: ComparisonType = ComparisonType.PATH,
    format: ExportFormat = None,
    orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
):
    service = ContributionComparisonService(orkg_backend)
    comparison = service.compare(
        contribution_ids=contributions,
        comparison_type=type,
        format=format,
    )

    if format == ExportFormat.CSV:
        return StreamingResponse(
            iter([comparison]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename={}.csv".format(
                    "_".join(contributions)
                )
            },
        )

    return ResponseWrapper.wrap_json(comparison)
