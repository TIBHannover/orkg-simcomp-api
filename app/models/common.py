# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel


class Response(BaseModel):
    timestamp: datetime
    uuid: UUID
    payload: Any


class Request(BaseModel):
    pass


class BaseORMObject(BaseModel):
    id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class OrkgResource(BaseModel):
    created_at: datetime
    created_by: str
    id: str


class OrkgObject(OrkgResource):
    _class: str
    datatype: Optional[str]
    label: str
    classes: Optional[List[str]]


class OrkgPredicate(OrkgResource):
    _class: str = "predicate"
    label: str
    description: Optional[str]


class OrkgSubject(OrkgResource):
    _class: str = "resource"
    classes: Optional[List[str]]
    extraction_method: Optional[str]
    featured: Optional[bool]
    formatted_label: Optional[str]
    label: str
    observatory_id: Optional[str]
    organization_id: Optional[str]
    shared: Optional[int]
    unlisted: Optional[bool]
    verified: Optional[bool]


class OrkgStatement(OrkgResource):
    object: OrkgObject
    predicate: OrkgPredicate
    subject: OrkgSubject
