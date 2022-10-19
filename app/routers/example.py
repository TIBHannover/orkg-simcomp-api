from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.util.decorators import log
from app.db.connection import get_db
from app.models.example import ExampleCreateResponse, ExampleCreateRequest, ExampleReadAllResponse
from app.services.example import ExampleService

router = APIRouter(
    prefix='/example',
    tags=['example']
)


@router.post('/', response_model=ExampleCreateResponse, status_code=200)
@log(__name__)
def creates_example(request: ExampleCreateRequest, db: Session = Depends(get_db)):
    service = ExampleService(db)
    return service.create(request.example.service_name, request.example.data)


@router.get('/', response_model=ExampleReadAllResponse, status_code=200)
@log(__name__)
def reads_all_examples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ExampleService(db)
    return service.read_all(skip=skip, limit=limit)
