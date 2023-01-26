import http

from fastapi.testclient import TestClient

from app.db.crud import CRUDService
from app.main import app
from tests.db.mock_crud import CRUDServiceMock

app.dependency_overrides[CRUDService.get_instance] = CRUDServiceMock.get_instance
client = TestClient(app)


def test_creates_link():
    long_url = 'https:/test.link.orkg?test=parameter&another=parameter'
    response = client.post('/shortener/', json={'long_url': long_url})

    _assert_create_response(response)


def test_creates_link_already_exist():
    long_url = 'https:/test.link.orkg?test=parameter&another=parameter'
    response = client.post('/shortener/', json={'long_url': long_url})
    _assert_create_response(response)

    id = response.json()['payload']['id']
    short_code = response.json()['payload']['short_code']

    response = client.post('/shortener/', json={'long_url': long_url})
    _assert_create_response(response)

    assert id == response.json()['payload']['id']
    assert short_code == response.json()['payload']['short_code']


def test_gets_link_success():
    long_url = 'https:/test.link.orkg?test=parameter&another=parameter'
    response = client.post('/shortener/', json={'long_url': long_url})
    _assert_create_response(response)

    short_code = response.json()['payload']['short_code']
    response = client.get('/shortener/', params={'short_code': short_code})
    _assert_get_response(response)


def test_gets_link_failure():
    short_code = 'unknown'
    response = client.get('/shortener/', params={'short_code': short_code})

    assert response.status_code == http.HTTPStatus.NOT_FOUND


def _assert_create_response(response):
    assert response.status_code == http.HTTPStatus.OK
    assert 'payload' in response.json()

    assert 'id' in response.json()['payload']
    assert isinstance(response.json()['payload']['id'], str)

    assert 'short_code' in response.json()['payload']
    assert isinstance(response.json()['payload']['short_code'], str)


def _assert_get_response(response):
    assert response.status_code == http.HTTPStatus.OK
    assert 'payload' in response.json()

    assert 'link' in response.json()['payload']
    assert isinstance(response.json()['payload']['link'], dict)

    link = response.json()['payload']['link']
    assert 'id' in link
    assert isinstance(link['id'], str)

    assert 'long_url' in link
    assert isinstance(link['long_url'], str)

    assert 'short_code' in link
    assert isinstance(link['short_code'], str)
