from typing import Any, List
from uuid import UUID

from pydantic import BaseModel

from app.models.common import Request, Response, BaseORMObject


class BaseExample(BaseModel):
    service_name: str
    data: Any


class ExampleCreateRequest(Request):
    example: BaseExample


class ExampleCreateResponse(Response):

    class Payload(BaseModel):
        id: UUID

    payload: Payload


class ExampleReadAllResponse(Response):

    class Payload(BaseModel):

        class Example(BaseExample, BaseORMObject):
            # In case one enum value has been excluded and still exists in the DB, we still want to retrieve it.
            service_name: str

        examples: List[Example]

    payload: Payload
