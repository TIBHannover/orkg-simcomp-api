import http

import pytest
from fastapi.testclient import TestClient

from app.db.crud import CRUDService
from app.main import app
from tests.common.assertion import assert_keys_in_dict
from tests.db.mock_crud import CRUDServiceMock

app.dependency_overrides[CRUDService.get_instance] = CRUDServiceMock.get_instance
client = TestClient(app)
thing = {
    'thing_type': 'Review',
    'thing_key': 'R123',
    'data': {'test': 'data'}
}


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # clear the db before each test but keep it initialized within the same test.
    next(CRUDServiceMock.get_instance()).db = {}
    yield
    pass


def test_adds_thing():
    response = client.post('/storage/thing', json=thing)
    assert response.status_code == http.HTTPStatus.CREATED


def test_adds_thing_already_exist():
    response_1 = client.post('/storage/thing', json=thing)
    assert response_1.status_code == http.HTTPStatus.CREATED

    response_2 = client.post('/storage/thing', json=thing)
    assert response_2.status_code == http.HTTPStatus.CONFLICT


def test_add_two_things_same_id_different_type():
    thing_2 = thing.copy()
    thing_2['thing_type'] = 'another_type'

    response_1 = client.post('/storage/thing', json=thing)
    assert response_1.status_code == http.HTTPStatus.CREATED

    response_2 = client.post('/storage/thing', json=thing_2)
    assert response_2.status_code == http.HTTPStatus.CREATED


def test_gets_thing_success():
    response = client.post('/storage/thing', json=thing)

    assert response.status_code == http.HTTPStatus.CREATED

    response = client.get('/storage/thing', params={'thing_type': thing['thing_type'], 'thing_key': thing['thing_key']})
    _assert_get_response(thing, response)


def test_gets_thing_failure():
    thing_type = 'unknown'
    thing_key = 'unknown'
    response = client.get('/storage/thing', params={'thing_type': thing_type, 'thing_key': thing_key})
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def _assert_get_response(target_thing, response):
    assert response.status_code == http.HTTPStatus.OK
    assert 'payload' in response.json()

    assert_keys_in_dict(response.json()['payload'], {
        'thing': dict
    })

    actual_thing = response.json()['payload']['thing']
    assert_keys_in_dict(actual_thing, {
        'id': str,
        'thing_type': str,
        'thing_key': str,
        'data': dict
    }, exact=False)

    assert actual_thing['thing_type'] == target_thing['thing_type']
    assert actual_thing['thing_key'] == target_thing['thing_key']
    assert actual_thing['data'] == target_thing['data']

