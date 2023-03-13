# -*- coding: utf-8 -*-
import http
import os
from typing import Any, Dict

from app.common.errors import OrkgSimCompApiError
from app.db.crud import CRUDService
from app.db.models.thing import Thing
from app.models.thing import ExportFormat, ThingType
from app.services.common.base import OrkgSimCompApiService
from app.services.thing.export import ComparisonExporter
from app.services.thing.export.review import ReviewExporter


class ThingService(OrkgSimCompApiService):
    def __init__(self, crud_service: CRUDService):
        super().__init__(logger_name=__name__)

        self.crud_service = crud_service

    def add_thing(
        self, thing_type: ThingType, thing_key: str, data: Dict[str, Any], config: Dict[str, Any]
    ):
        if thing_type == ThingType.UNKNOWN and os.environ.get("ORKG_SIMCOMP_API_ENV") != "test":
            raise OrkgSimCompApiError(
                message='thing_type="{}" is only allowed for test usage.'.format(thing_type),
                cls=self.__class__,
                status_code=http.HTTPStatus.BAD_REQUEST,
            )

        thing = self.crud_service.get_row_by(
            entity=Thing,
            columns_values={
                "thing_type": thing_type,
                "thing_key": thing_key,
            },
        )

        if thing:
            raise OrkgSimCompApiError(
                message='Thing with thing_type="{}" and thing_key="{}" already exists.'.format(
                    thing_type, thing_key
                ),
                cls=self.__class__,
                status_code=http.HTTPStatus.CONFLICT,
            )

        # TODO: shall we check whether the data object is parseable if we already know its ThingType ? In doing so we
        #   enhance the data validity.

        thing = Thing(thing_type=thing_type, thing_key=thing_key, data=data, config=config)
        self.crud_service.create(entity=thing)

    def get_thing(
        self,
        thing_type: ThingType,
        thing_key: str,
    ):
        thing = self.crud_service.get_row_by(
            entity=Thing,
            columns_values={
                "thing_type": thing_type,
                "thing_key": thing_key,
            },
        )

        if thing:
            return {"thing": thing}

        raise OrkgSimCompApiError(
            message='Thing with thing_type="{}" and thing_key="{}" not found.'.format(
                thing_type, thing_key
            ),
            cls=self.__class__,
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    def export_thing(self, thing_type: ThingType, thing_key: str, format: ExportFormat, **kwargs):
        thing = self.get_thing(thing_type, thing_key)["thing"]

        try:
            return {ThingType.COMPARISON: ComparisonExporter, ThingType.REVIEW: ReviewExporter}[
                thing_type
            ].export(thing.data, format, thing.config, self, **kwargs)
        except KeyError:
            raise OrkgSimCompApiError(
                message='Exporting thing with thing_type="{}" is not supported'.format(thing_type),
                cls=self.__class__,
                status_code=http.HTTPStatus.NOT_IMPLEMENTED,
            )
