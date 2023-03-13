# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field, validator

from app.models.common import BaseORMObject, Request, Response


class ThingType(str, Enum):
    UNKNOWN = "UNKNOWN"  # for testing purposes
    COMPARISON = "COMPARISON"
    DIAGRAM = "DIAGRAM"
    VISUALIZATION = "VISUALIZATION"
    DRAFT_COMPARISON = "DRAFT_COMPARISON"
    LIST = "LIST"
    REVIEW = "REVIEW"
    QUALITY_REVIEW = "QUALITY_REVIEW"
    PAPER_VERSION = "PAPER_VERSION"
    ANY = "ANY"


class ExportFormat(str, Enum):
    UNKNOWN = "UNKNOWN"  # for testing purposes
    CSV = "CSV"
    DATAFRAME = "DATAFRAME"
    HTML = "HTML"
    XML = "XML"


class BaseThing(Request):
    thing_type: ThingType
    thing_key: str = Field(..., min_length=1)
    config: Dict[str, Any] = {}


class ThingAddRequest(BaseThing):
    data: Dict[str, Any]

    @validator("data", pre=True, always=True)
    def validate_data_dict(cls, value):
        if not value:
            raise ValueError('empty dict is not allowed for field "data"')
        return value


class ThingGetResponse(Response):
    class Payload(BaseModel):
        class Thing(BaseThing, BaseORMObject):
            data: Dict[str, Any]

        thing: Thing

    payload: Payload
