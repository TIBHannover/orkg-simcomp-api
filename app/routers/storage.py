import http

from fastapi import APIRouter, Depends

from app.common.util.decorators import log
from app.db.crud import CRUDService
from app.models.storage import StorageThingAddRequest, StorageThingGetResponse
from app.services.storage import StorageService

router = APIRouter(
    prefix='/storage',
    tags=['storage']
)


@router.post('/thing', status_code=http.HTTPStatus.CREATED)
@log(__name__)
def adds_thing(
        request: StorageThingAddRequest,
        crud_service: CRUDService = Depends(CRUDService.get_instance)
):
    service = StorageService(crud_service)
    service.add_thing(request.thing_type, request.thing_key, request.data)


@router.get('/thing', response_model=StorageThingGetResponse, status_code=http.HTTPStatus.OK)
@log(__name__)
def gets_thing(
        thing_type: str,
        thing_key: str,
        crud_service: CRUDService = Depends(CRUDService.get_instance)
):
    service = StorageService(crud_service)
    return service.get_thing(thing_type, thing_key)
