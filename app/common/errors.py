from typing import Any, Type

from fastapi import HTTPException


class OrkgSimCompApiError(HTTPException):

    def __init__(self, message: str, cls: Type[Any]):
        super().__init__(status_code=500, detail=message)
        self.class_name = '{}.{}'.format(cls.__module__, cls.__name__)
