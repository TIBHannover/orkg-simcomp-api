# -*- coding: utf-8 -*-
import http

import pytest
from fastapi.testclient import TestClient

from app.db.crud import CRUDService
from app.main import app
from app.models.thing import ExportFormat, ThingType
from tests.common.assertion import assert_keys_in_dict
from tests.db.mock_crud import CRUDServiceMock

app.dependency_overrides[CRUDService.get_instance] = CRUDServiceMock.get_instance
client = TestClient(app)
thing: dict = {}


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # clear the db before each test but keep it initialized within the same test.
    next(CRUDServiceMock.get_instance()).db = {}

    global thing
    thing = {
        "thing_type": ThingType.COMPARISON.value,
        "thing_key": "R123",
        "data": {"test": "data"},
        "config": {"properties": ["P31", "P27"]},
    }

    yield


def test_adds_thing():
    response = client.post("/thing/", json=thing)
    assert response.status_code == http.HTTPStatus.CREATED


def test_adds_thing_already_exist():
    response_1 = client.post("/thing/", json=thing)
    assert response_1.status_code == http.HTTPStatus.CREATED

    response_2 = client.post("/thing/", json=thing)
    assert response_2.status_code == http.HTTPStatus.CONFLICT


def test_add_two_things_same_id_different_type():
    thing_2 = thing.copy()
    thing_2["thing_type"] = ThingType.DIAGRAM.value

    response_1 = client.post("/thing/", json=thing)
    assert response_1.status_code == http.HTTPStatus.CREATED

    response_2 = client.post("/thing/", json=thing_2)
    assert response_2.status_code == http.HTTPStatus.CREATED


def test_gets_thing_success():
    response = client.post("/thing/", json=thing)

    assert response.status_code == http.HTTPStatus.CREATED

    response = client.get(
        "/thing/",
        params={
            "thing_type": thing["thing_type"],
            "thing_key": thing["thing_key"],
        },
    )
    _assert_get_response(thing, response)


def test_gets_thing_failure():
    thing_type = ThingType.COMPARISON.value
    thing_key = "unknown"
    response = client.get(
        "/thing/",
        params={
            "thing_type": thing_type,
            "thing_key": thing_key,
        },
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_exports_thing_unknown_type():
    thing["thing_type"] = ThingType.UNKNOWN.value
    format = ExportFormat.DATAFRAME.value

    response = client.post("/thing/", json=thing)
    assert response.status_code == http.HTTPStatus.CREATED

    response = client.get(
        "/thing/export",
        params={
            "thing_type": thing["thing_type"],
            "thing_key": thing["thing_key"],
            "format": format,
        },
    )
    assert response.status_code == http.HTTPStatus.NOT_IMPLEMENTED


def test_exports_thing_unknown_format():
    format = ExportFormat.UNKNOWN.value
    thing["data"] = {
        "contributions": [],
        "predicates": [],
        "data": {},
    }

    response = client.post("/thing/", json=thing)
    assert response.status_code == http.HTTPStatus.CREATED

    response = client.get(
        "/thing/export",
        params={
            "thing_type": thing["thing_type"],
            "thing_key": thing["thing_key"],
            "format": format,
        },
    )
    assert response.status_code == http.HTTPStatus.NOT_IMPLEMENTED


def test_exports_thing_success_normal_response():
    format = ExportFormat.DATAFRAME.value
    thing["data"] = {
        "contributions": [],
        "predicates": [],
        "data": {},
    }

    response = client.post("/thing/", json=thing)
    assert response.status_code == http.HTTPStatus.CREATED

    response = client.get(
        "/thing/export",
        params={
            "thing_type": thing["thing_type"],
            "thing_key": thing["thing_key"],
            "format": format,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


def test_exports_thing_success_streaming_response():
    format = ExportFormat.CSV.value
    thing["data"] = {
        "contributions": [],
        "predicates": [],
        "data": {},
    }

    response = client.post("/thing/", json=thing)
    assert response.status_code == http.HTTPStatus.CREATED

    response = client.get(
        "/thing/export",
        params={
            "thing_type": thing["thing_type"],
            "thing_key": thing["thing_key"],
            "format": format,
        },
    )

    assert response.status_code == http.HTTPStatus.OK
    assert "content-disposition" in response.headers
    assert response.headers["content-disposition"] == "attachment; filename={}_{}.csv".format(
        thing["thing_type"].lower(),
        thing["thing_key"],
    )


def _assert_get_response(target_thing, response):
    assert response.status_code == http.HTTPStatus.OK
    assert "payload" in response.json()

    assert_keys_in_dict(
        response.json()["payload"],
        {"thing": dict},
    )

    actual_thing = response.json()["payload"]["thing"]
    assert_keys_in_dict(
        actual_thing,
        {"id": str, "thing_type": str, "thing_key": str, "data": dict, "config": dict},
        exact=False,
    )

    assert actual_thing["thing_type"] == target_thing["thing_type"]
    assert actual_thing["thing_key"] == target_thing["thing_key"]
    assert actual_thing["data"] == target_thing["data"]
    assert actual_thing["config"] == target_thing["config"]
