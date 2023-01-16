# Contributors Guidelines
> Note: this document is currently under construction.

[//]: # (add some text here)

## Tools and Frameworks

[//]: # (add some text here)

* PyCharm
* Poetry
* FastAPI
* PyTest

## Project file structure

[//]: # (add some text here)

## Request and Response conventions

[//]: # (add some text here)

## How to add a new service

This is an example of a service that simply stores a new Example item in the database.

### `routers/example.py`

```python
router = APIRouter(
    prefix='/example',
    tags=['example']
)


@router.post('/item', response_model=ExampleCreateItemResponse, status_code=200)
@log(__name__)
def creates_example_item(
        request: ExampleCreateItemRequest,
        crud_service: CRUDService = Depends(CRUDService.get_instance)
):
    service = ShortenerService(crud_service)
    return service.create_example_item(request.name)
```

### `models/example.py`

```python
class ExampleCreateItemRequest(Request):
    name: str

class ExampleCreateItemResponse(Response):

    class Payload(BaseModel):
        id: UUID
        name: str

    payload: Payload
```

### `services/example/service.py`

```python
class ExampleService(OrkgSimCompApiService):

    def __init__(self, crud_service: CRUDService):
        super().__init__(logger_name=__name__)

        self.crud_service = crud_service

    def create_example_item(self, name: str):
        item = self.crud_service.get_row_by(entity=Item, column='name', value=name)

        if item:
            return ResponseWrapper.wrap_json({
                'id': item.id,
                'name': item.name
            })

        item = Item(name=name)
        self.crud_service.create(entity=item)

        return ResponseWrapper.wrap_json({
                'id': item.id,
                'name': item.name
        })
```

### `db/models/example.py`

```python
class Item(Base, BaseTable):
    __tablename__ = 'examples'

    name = Column(String, nullable=False)
```

##  How to test your service

### `tests/routers/test_example.py`

```python
app.dependency_overrides[CRUDService.get_instance] = CRUDServiceMock.get_instance
client = TestClient(app)


def test_creates_link():
    name = 'item_name'
    response = client.post('/example/item', json={'name': name})

    assert response.status_code == 200
    assert 'payload' in response.json()

    assert 'id' in response.json()['payload']n
    assert isinstance(response.json()['payload']['id'], str)

    assert 'name' in response.json()['payload']
    assert isinstance(response.json()['payload']['name'], str)
```

