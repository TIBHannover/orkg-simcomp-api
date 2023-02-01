import http

from typing import List

from fastapi import APIRouter, Depends, Query

from app.models.contribution import ContributionSimilarityInitIndexResponse, ContributionSimilarityIndexResponse, \
    ContributionSimilaritySimilarResponse, ContributionComparisonResponse, ComparisonType
from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.common.es import ElasticsearchService
from app.common.util.decorators import log
from app.services.contribution import ContributionSimilarityService, ContributionComparisonService

router = APIRouter(
    prefix='/contribution',
    tags=['contribution']
)


@router.post('/internal/init', response_model=ContributionSimilarityInitIndexResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def initializes_es_index(
        orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
        es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance)
):
    service = ContributionSimilarityService(orkg_backend, es_service)
    return service.init_index()


@router.post('/internal/index', response_model=ContributionSimilarityIndexResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def indexes_a_contribution(
        contribution_id: str,
        orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
        es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance)
):
    service = ContributionSimilarityService(orkg_backend, es_service)
    return service.index(contribution_id)


@router.get('/similar', response_model=ContributionSimilaritySimilarResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def queries_similar_contributions(
        contribution_id: str,
        n_results: int = 10,
        orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
        es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance)
):
    service = ContributionSimilarityService(orkg_backend, es_service)
    return service.query(contribution_id, n_results)


@router.get('/compare', response_model=ContributionComparisonResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def compares_contributions(
        contributions: List[str] = Query(None),
        type: ComparisonType = ComparisonType.PATH,
        orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance)
):
    service = ContributionComparisonService(orkg_backend)
    return service.compare(contribution_ids=contributions, comparison_type=type)
