# -*- coding: utf-8 -*-
from typing import Any, Type

from fastapi import HTTPException


class OrkgSimCompApiError(HTTPException):
    def __init__(
        self,
        message: str,
        cls: Type[Any],
        status_code=500,
    ):
        super().__init__(
            status_code=status_code,
            detail=message,
        )
        self.class_name = "{}.{}".format(cls.__module__, cls.__name__)
