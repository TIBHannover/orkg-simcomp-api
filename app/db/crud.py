# -*- coding: utf-8 -*-
from typing import List, Type

from sqlalchemy.orm import Session

from app.db.connection import Base, get_db
from app.services.common.base import OrkgSimCompApiService


class CRUDService(OrkgSimCompApiService):
    def __init__(self, db: Session = get_db()):
        super().__init__(logger_name=__name__)

        self.db = db

    @staticmethod
    def get_instance():
        yield CRUDService()

    def create(self, entity: Base):
        self.logger.debug("Creating entity...")

        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

        self.logger.debug("Entity created!")

    def query_all(
        self,
        entity: Type[Base],
        skip: int,
        limit: int,
    ) -> List[Base]:
        self.logger.debug("Querying entities...")

        return self.db.query(entity).offset(skip).limit(limit).all()

    def count_all(self, entity: Type[Base]) -> int:
        self.logger.debug("Counting entities...")

        return self.db.query(entity).count()

    def get_row_by(
        self,
        entity: Type[Base],
        columns_values: dict,
    ) -> Base:
        return self.db.query(entity).filter_by(**columns_values).first()

    def exists(
        self,
        entity: Type[Base],
        columns_values: dict,
    ) -> bool:
        return bool(self.get_row_by(entity, columns_values))
