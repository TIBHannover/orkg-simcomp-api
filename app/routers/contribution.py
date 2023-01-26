import http

from fastapi import APIRouter, Depends

from app.models.contribution import ContributionSimilarityInitIndexResponse, ContributionSimilarityIndexResponse, \
    ContributionSimilaritySimilarResponse
from app.services.common.orkg_backend import OrkgBackendWrapperService
from app.services.common.es import ElasticsearchService
from app.common.util.decorators import log
from app.services.contribution import ContributionService

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
    service = ContributionService(orkg_backend, es_service)
    return service.init_index()


@router.post('/internal/index', response_model=ContributionSimilarityIndexResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def indexes_a_contribution(
        contribution_id: str,
        orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
        es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance)
):
    service = ContributionService(orkg_backend, es_service)
    return service.index(contribution_id)


@router.get('/similar', response_model=ContributionSimilaritySimilarResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def queries_similar_contributions(
        contribution_id: str,
        n_results: int = 10,
        orkg_backend: OrkgBackendWrapperService = Depends(OrkgBackendWrapperService.get_instance),
        es_service: ElasticsearchService = Depends(ElasticsearchService.get_instance)
):
    service = ContributionService(orkg_backend, es_service)
    return service.query(contribution_id, n_results)
