from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Response(BaseModel):
    timestamp: datetime
    uuid: UUID


class Request(BaseModel):
    pass


class BaseORMObject(BaseModel):

    id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
