# -*- coding: utf-8 -*-
from fastapi import HTTPException

from app.common.util.hashing import hash_base62
from app.db.crud import CRUDService
from app.db.models.link import Link
from app.services.common.base import OrkgSimCompApiService


class ShortenerService(OrkgSimCompApiService):
    def __init__(self, crud_service: CRUDService):
        super().__init__(logger_name=__name__)

        self.crud_service = crud_service

    def create_link(self, long_url: str):
        link = self.crud_service.get_row_by(
            entity=Link,
            columns_values={"long_url": long_url},
        )

        if link:
            return {
                "id": link.id,
                "short_code": link.short_code,
            }

        short_code = self._generate_next_short_code()
        link = Link(
            long_url=long_url,
            short_code=short_code,
        )
        self.crud_service.create(entity=link)

        return {
            "id": link.id,
            "short_code": link.short_code,
        }

    def get_link(self, short_code: str):
        link = self.crud_service.get_row_by(
            entity=Link,
            columns_values={"short_code": short_code},
        )

        if link:
            return {"link": link}

        raise HTTPException(
            status_code=404,
            detail='Link with short_code="{}" not found.'.format(short_code),
        )

    def _generate_next_short_code(self):
        base_id = self.crud_service.count_all(entity=Link)

        short_code = hash_base62(base_id + 1)
        while self.crud_service.exists(
            entity=Link,
            columns_values={"short_code": short_code},
        ):
            base_id += 1
            short_code = hash_base62(base_id)

        return short_code
