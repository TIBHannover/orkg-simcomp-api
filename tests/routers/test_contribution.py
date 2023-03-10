# -*- coding: utf-8 -*-
import http

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.thing import ExportFormat
from app.services.common.es import ElasticsearchService
from app.services.common.orkg_backend import OrkgBackendWrapperService
from tests.common.assertion import assert_keys_in_dict
from tests.mock.mock_es import ElasticsearchServiceMock
from tests.mock.mock_orkg_backend import OrkgBackendWrapperServiceMock

app.dependency_overrides[
    OrkgBackendWrapperService.get_instance
] = OrkgBackendWrapperServiceMock.get_instance
app.dependency_overrides[ElasticsearchService.get_instance] = ElasticsearchServiceMock.get_instance
client = TestClient(app)


def test_initializes_es_index():
    response = client.post("/contribution/internal/init")

    assert response.status_code == http.HTTPStatus.OK
    assert "payload" in response.json()

    assert_keys_in_dict(
        response.json()["payload"],
        {
            "n_contributions": int,
            "n_indexed_contributions": int,
            "not_indexed_contributions": list,
        },
    )

    assert response.json()["payload"]["n_contributions"] == 3
    assert response.json()["payload"]["n_indexed_contributions"] == 3
    assert len(response.json()["payload"]["not_indexed_contributions"]) == 0


def test_indexes_a_contribution_success():
    _indexes_a_contribution(contribution_id="123", succeeded=True)


def test_indexes_a_contribution_failure():
    _indexes_a_contribution(
        contribution_id="random_id",
        succeeded=False,
    )


def test_queries_similar_contributions_success():
    _queries_similar_contributions(contribution_id="123", succeeded=True)


def test_queries_similar_contributions_failure():
    _queries_similar_contributions(
        contribution_id="random_id",
        succeeded=False,
    )


def test_compares_contributions_path_unknown_ids_fails():
    _compares_contributions(
        contribution_ids=["unknown", "unknown"],
        comparison_type="path",
        succeeded=False,
    )


def test_compares_contributions_path_success():
    _compares_contributions(
        contribution_ids=["123", "234", "345"],
        comparison_type="path",
        succeeded=True,
    )


def test_compares_contributions_merge_success():
    _compares_contributions(
        contribution_ids=["123", "234", "345"],
        comparison_type="merge",
        succeeded=True,
    )


# TODO: why is it failing ?
@pytest.mark.skip(reason="Issue with 'weakref' after updating to a newer fastapi version.")
def test_compares_contributions_format_dataframe():
    contribution_ids = ["123", "234", "345"]
    comparison_type = "path"
    format = ExportFormat.DATAFRAME.value

    response = client.get(
        "/contribution/compare",
        params={
            "contributions": ",".join(contribution_ids),
            "type": comparison_type,
            "format": format,
        },
    )

    assert response.status_code == http.HTTPStatus.OK
    assert "payload" in response.json()
    assert isinstance(response.json()["payload"], dict)


def test_compares_contributions_format_csv():
    contribution_ids = ["123", "234", "345"]
    comparison_type = "path"
    format = ExportFormat.CSV.value

    response = client.get(
        "/contribution/compare",
        params={
            "contributions": ",".join(contribution_ids),
            "type": comparison_type,
            "format": format,
        },
    )

    assert response.status_code == http.HTTPStatus.OK
    assert "content-disposition" in response.headers
    assert response.headers["content-disposition"] == "attachment; filename={}.csv".format(
        "_".join(contribution_ids)
    )


def _indexes_a_contribution(contribution_id, succeeded):
    response = client.post(
        "/contribution/internal/index",
        params={"contribution_id": contribution_id},
    )

    assert response.status_code == http.HTTPStatus.OK
    assert "payload" in response.json()

    assert "message" in response.json()["payload"]

    if succeeded:
        assert response.json()["payload"]["message"] == "Contribution {} indexed".format(
            contribution_id
        )
    else:
        assert response.json()["payload"]["message"] == "Contribution {} unknown or empty".format(
            contribution_id
        )


def _queries_similar_contributions(contribution_id, succeeded):
    response = client.get(
        "/contribution/similar",
        params={
            "contribution_id": contribution_id,
            "n_results": 2,
        },
    )

    assert response.status_code == http.HTTPStatus.OK
    assert "payload" in response.json()

    assert "contributions" in response.json()["payload"]
    assert isinstance(
        response.json()["payload"]["contributions"],
        list,
    )

    assert_keys_in_dict(
        response.json()["payload"],
        {"contributions": list},
    )

    if succeeded:
        assert len(response.json()["payload"]["contributions"]) == 2
    else:
        assert len(response.json()["payload"]["contributions"]) == 0

    for contribution in response.json()["payload"]["contributions"]:
        assert_keys_in_dict(
            contribution,
            {
                "id": str,
                "label": str,
                "paper_id": str,
                "paper_label": str,
                "similarity_percentage": float,
            },
        )


def _compares_contributions(contribution_ids, comparison_type, succeeded):
    response = client.get(
        "/contribution/compare",
        params={
            "contributions": ",".join(contribution_ids),
            "type": comparison_type,
        },
    )

    assert response.status_code == 200
    assert "payload" in response.json()
    assert "comparison" in response.json()["payload"]

    comparison = response.json()["payload"]["comparison"]
    assert isinstance(comparison, dict)

    assert_keys_in_dict(
        comparison,
        {
            "contributions": list,
            "predicates": list,
            "data": dict,
        },
    )

    if not succeeded:
        assert len(comparison["contributions"]) == 0
        assert len(comparison["predicates"]) == 0
        assert len(comparison["data"].keys()) == 0

    for contribution in comparison["contributions"]:
        assert_keys_in_dict(
            contribution,
            {
                "id": str,
                "label": str,
                "paper_id": str,
                "paper_label": str,
                "paper_year": str,
            },
        )

    for predicate in comparison["predicates"]:
        assert_keys_in_dict(
            predicate,
            {
                "id": str,
                "label": str,
                "n_contributions": int,
                "active": bool,
                "similar_predicates": list,
            },
        )

    for (
        pathed_predicate,
        contributions,
    ) in comparison["data"].items():
        assert isinstance(pathed_predicate, str)
        assert isinstance(contributions, list)
        assert len(contributions) == len(comparison["contributions"])

        for contribution in contributions:
            assert isinstance(contribution, list)
            assert len(contribution) > 0

            for target in contribution:
                assert isinstance(target, dict)

                if not target:
                    continue

                assert_keys_in_dict(
                    target,
                    {
                        "id": str,
                        "label": str,
                        "type": str,
                        "classes": list,
                        "path": list,
                        "path_labels": list,
                    },
                )
