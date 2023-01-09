from typing import Dict, Any

from sqlalchemy.orm import Session

from app.services.common.base import OrkgSimCompApiService
from app.services.common.wrapper import ResponseWrapper
from app.db import crud
from app.db.models.example import Example


class ExampleService(OrkgSimCompApiService):

    def __init__(self, db: Session):
        super().__init__(logger_name=__name__)

        self.n_fields = 3
        self.db = db

    def create(self, service_name: str, data: Dict[str, Any]):

        example = Example(service_name=service_name, data=data)
        crud.create(self.db, example)

        return ResponseWrapper.wrap_json({'id': example.id})

    def read_all(self, skip: int = 0, limit: int = 100):
        examples = crud.query_all(self.db, Example, skip, limit)
        return ResponseWrapper.wrap_json({'examples': examples})
