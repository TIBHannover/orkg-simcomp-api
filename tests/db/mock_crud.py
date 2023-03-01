# -*- coding: utf-8 -*-
from typing import Dict, List, Type

from app.db.connection import Base
from tests.mock.mock_base import OrkgSimCompApiServiceMock


class CRUDServiceMock(OrkgSimCompApiServiceMock):
    def __init__(self):
        if not hasattr(self, "db"):
            # TODO: the current singleton approach does not provide a possibility not to call __init__() after calling
            #    __new__(), which leads to initiating self.db with an empty dict again and losing the information stored
            #   by an earlier test request. Therefore, a better singleton approach is required, that prevents __init__()
            #   from being called more than once.
            self.db: Dict[Type[Base], List[Base]] = {}

    @staticmethod
    def get_instance():
        yield CRUDServiceMock()

    def create(self, entity: Base):
        if not type(entity) in self.db:
            self.db[type(entity)] = []

        entity = self.__instantiate_defaults(entity)

        self.db[type(entity)].append(entity)

    def query_all(
        self,
        entity: Type[Base],
        skip: int,
        limit: int,
    ):
        if entity not in self.db:
            return []

        return self.db[entity][skip:][:limit]

    def count_all(self, entity: Type[Base]):
        if entity not in self.db:
            return 0

        return len(self.db[entity])

    def get_row_by(
        self,
        entity: Type[Base],
        columns_values: dict,
    ):
        if entity not in self.db:
            return None

        for instance in self.db[entity]:
            for (
                column,
                value,
            ) in columns_values.items():
                if instance.__getattribute__(column) != value:
                    return None

            return instance

        return None

    def exists(
        self,
        entity: Type[Base],
        columns_values: dict,
    ):
        return bool(self.get_row_by(entity, columns_values))

    @staticmethod
    def __instantiate_defaults(entity: Base):
        for column in entity.__mapper__.mapper.columns:
            if column.default:
                entity.__setattr__(
                    column.name,
                    column.default.arg(None),
                )

        return entity
