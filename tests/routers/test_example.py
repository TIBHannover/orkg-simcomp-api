from fastapi.testclient import TestClient

from app.db.connection import get_db
from app.main import app
from tests.db.connection import override_get_db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_creates_example_ok():
    example = {'service_name': 'COMPARISON', 'data': {'hello': 'world'}}
    response = client.post('/example/', json={'example': example})

    assert response.status_code == 200
    assert 'payload' in response.json()
    assert 'id' in response.json()['payload']
    assert isinstance(response.json()['payload']['id'], str)


def test_reads_all_examples_ok():
    response = client.get('/example/', params={'skip': 0, 'limit': 100})

    assert response.status_code == 200
    assert 'payload' in response.json()
    assert 'examples' in response.json()['payload']
    assert isinstance(response.json()['payload']['examples'], list)

    for example in response.json()['payload']['examples']:
        assert 'id' in example
        assert 'service_name' in example
        assert 'data' in example
