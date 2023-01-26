from typing import Any, Dict

from pydantic import BaseModel, Field, validator

from app.models.common import Request, Response, BaseORMObject


class BaseThing(Request):
    thing_type: str = Field(..., min_length=1)
    thing_key: str = Field(..., min_length=1)


class StorageThingAddRequest(BaseThing):
    data: Dict[str, Any]

    @validator('data', pre=True, always=True)
    def validate_data_dict(cls, value):
        if not value:
            raise ValueError('empty dict is not allowed for field "data"')
        return value


class StorageThingGetResponse(Response):

    class Payload(BaseModel):

        class Thing(BaseThing, BaseORMObject):
            data: Dict[str, Any]

        thing: Thing

    payload: Payload
