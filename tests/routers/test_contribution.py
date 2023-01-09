from fastapi.testclient import TestClient

from app.main import app
from app.services.common.es import ElasticsearchService
from app.services.common.orkg_backend import OrkgBackendWrapperService
from tests.mock.mock_es import ElasticsearchServiceMock
from tests.mock.mock_orkg_backend import OrkgBackendWrapperServiceMock

app.dependency_overrides[OrkgBackendWrapperService.get_instance] = OrkgBackendWrapperServiceMock.get_instance
app.dependency_overrides[ElasticsearchService.get_instance] = ElasticsearchServiceMock.get_instance
client = TestClient(app)


def test_initializes_es_index():
    response = client.post('/contribution/internal/init')

    assert response.status_code == 200
    assert 'payload' in response.json()

    assert 'n_contributions' in response.json()['payload']
    assert isinstance(response.json()['payload']['n_contributions'], int)
    assert response.json()['payload']['n_contributions'] == 3

    assert 'n_indexed_contributions' in response.json()['payload']
    assert isinstance(response.json()['payload']['n_indexed_contributions'], int)
    assert response.json()['payload']['n_indexed_contributions'] == 3

    assert 'not_indexed_contributions' in response.json()['payload']
    assert isinstance(response.json()['payload']['not_indexed_contributions'], list)
    assert len(response.json()['payload']['not_indexed_contributions']) == 0


def test_indexes_a_contribution_success():
    _indexes_a_contribution(contribution_id='123', succeeded=True)


def test_indexes_a_contribution_failure():
    _indexes_a_contribution(contribution_id='random_id', succeeded=False)


def test_queries_similar_contributions_success():
    _queries_similar_contributions(contribution_id='123', succeeded=True)


def test_queries_similar_contributions_failure():
    _queries_similar_contributions(contribution_id='random_id', succeeded=False)


def _indexes_a_contribution(contribution_id, succeeded):
    response = client.post('/contribution/internal/index', params={'contribution_id': contribution_id})

    assert response.status_code == 200
    assert 'payload' in response.json()

    assert 'message' in response.json()['payload']

    if succeeded:
        assert response.json()['payload']['message'] == 'Contribution {} indexed'.format(contribution_id)
    else:
        assert response.json()['payload']['message'] == 'Contribution {} unknown or empty'.format(contribution_id)


def _queries_similar_contributions(contribution_id, succeeded):
    response = client.get('/contribution/similar', params={'contribution_id': contribution_id, 'n_results': 2})

    assert response.status_code == 200
    assert 'payload' in response.json()

    assert 'contributions' in response.json()['payload']
    assert isinstance(response.json()['payload']['contributions'], list)

    if succeeded:
        assert len(response.json()['payload']['contributions']) == 2
    else:
        assert len(response.json()['payload']['contributions']) == 0

    for contribution in response.json()['payload']['contributions']:
        assert 'id' in contribution
        assert isinstance(contribution['id'], str)

        assert 'label' in contribution
        assert isinstance(contribution['label'], str)

        assert 'paper_id' in contribution
        assert isinstance(contribution['paper_id'], str)

        assert 'paper_label' in contribution
        assert isinstance(contribution['paper_label'], str)

        assert 'similarity_percentage' in contribution
        assert isinstance(contribution['similarity_percentage'], float)
