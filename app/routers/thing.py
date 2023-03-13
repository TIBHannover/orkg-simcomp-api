# -*- coding: utf-8 -*-
import http

import fastapi
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.common.util.decorators import log
from app.db.crud import CRUDService
from app.models.common import Response
from app.models.thing import ExportFormat, ThingAddRequest, ThingGetResponse, ThingType
from app.services.common.wrapper import ResponseWrapper
from app.services.thing import ThingService

router = APIRouter(prefix="/thing", tags=["thing"])


@router.post("/", status_code=http.HTTPStatus.CREATED)
@log(__name__)
def adds_thing(
    request: ThingAddRequest,
    crud_service: CRUDService = Depends(CRUDService.get_instance),
):
    service = ThingService(crud_service)
    return ResponseWrapper.wrap_json(
        service.add_thing(request.thing_type, request.thing_key, request.data, request.config)
    )


@router.get(
    "/",
    response_model=ThingGetResponse,
    status_code=http.HTTPStatus.OK,
)
@log(__name__)
def gets_thing(
    thing_type: ThingType,
    thing_key: str,
    crud_service: CRUDService = Depends(CRUDService.get_instance),
):
    service = ThingService(crud_service)
    return ResponseWrapper.wrap_json(service.get_thing(thing_type, thing_key))


@router.get(
    "/export",
    response_model=Response,
    status_code=http.HTTPStatus.OK,
)
@log(__name__)
def exports_thing(
    thing_type: ThingType,
    thing_key: str,
    format: ExportFormat,
    like_ui: bool = False,
    crud_service: CRUDService = Depends(CRUDService.get_instance),
):
    service = ThingService(crud_service)
    export = service.export_thing(thing_type, thing_key, format, like_ui=like_ui)

    if format == ExportFormat.CSV:
        return StreamingResponse(
            iter([export]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename={}_{}.csv".format(
                    thing_type.lower(), thing_key
                )
            },
        )

    if format == ExportFormat.XML:
        return fastapi.Response(content=export, media_type="application/xml")

    return ResponseWrapper.wrap_json(export)
