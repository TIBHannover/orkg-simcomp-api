import http

from fastapi.exceptions import HTTPException
from typing import Any, Dict

from starlette.responses import JSONResponse

from app.common.errors import OrkgSimCompApiError
from app.db.crud import CRUDService
from app.db.models.storage import Thing
from app.services.common.base import OrkgSimCompApiService
from app.services.common.wrapper import ResponseWrapper


class StorageService(OrkgSimCompApiService):

    def __init__(self, crud_service: CRUDService):
        super().__init__(logger_name=__name__)

        self.crud_service = crud_service

    def add_thing(self, thing_type: str, thing_key: str, data: Dict[str, Any]):
        thing = self.crud_service.get_row_by(
            entity=Thing,
            columns_values={
                'thing_type': thing_type,
                'thing_key': thing_key
            }
        )

        if thing:
            raise OrkgSimCompApiError(
                message='Thing with thing_type="{}" and thing_key="{}" already exists.'.format(thing_type, thing_key),
                cls=self.__class__,
                status_code=http.HTTPStatus.CONFLICT
            )

        thing = Thing(thing_type=thing_type, thing_key=thing_key, data=data)
        self.crud_service.create(entity=thing)

    def get_thing(self, thing_type: str, thing_key: str):
        thing = self.crud_service.get_row_by(
            entity=Thing,
            columns_values={
                'thing_type': thing_type,
                'thing_key': thing_key
            }
        )

        if thing:
            return ResponseWrapper.wrap_json({'thing': thing})

        raise OrkgSimCompApiError(
            message='Thing with thing_type="{}" and thing_key="{}" not found.'.format(thing_type, thing_key),
            cls=self.__class__,
            status_code=http.HTTPStatus.NOT_FOUND
        )
