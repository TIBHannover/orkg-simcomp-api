from uuid import UUID
from pydantic import BaseModel

from app.models.common import Response, Request, BaseORMObject


class ShortenerCreateLinkRequest(Request):
    long_url: str


class ShortenerCreateLinkResponse(Response):

    class Payload(BaseModel):
        id: UUID
        short_code: str

    payload: Payload


class ShortenerGetLinkResponse(Response):

    class Payload(BaseModel):

        class Link(BaseORMObject):
            long_url: str
            short_code: str

        link: Link

    payload: Payload
