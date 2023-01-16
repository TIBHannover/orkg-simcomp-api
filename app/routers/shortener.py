from fastapi import APIRouter, Depends

from app.common.util.decorators import log
from app.db.crud import CRUDService
from app.models.shortener import ShortenerCreateLinkRequest, ShortenerCreateLinkResponse, ShortenerGetLinkResponse
from app.services.shortener import ShortenerService

router = APIRouter(
    prefix='/shortener',
    tags=['shortener']
)


@router.post('/', response_model=ShortenerCreateLinkResponse, status_code=200)
@log(__name__)
def creates_link(
        request: ShortenerCreateLinkRequest,
        crud_service: CRUDService = Depends(CRUDService.get_instance)
):
    service = ShortenerService(crud_service)
    return service.create_link(request.long_url)


@router.get('/', response_model=ShortenerGetLinkResponse, status_code=200)
@log(__name__)
def gets_link(
        short_code,
        crud_service: CRUDService = Depends(CRUDService.get_instance)
):
    service = ShortenerService(crud_service)
    return service.get_link(short_code)
