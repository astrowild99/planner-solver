"""
this tests the apis directly
"""

import pytest
from starlette.testclient import TestClient

from planner_solver.api import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_api_healthcheck(
        client
):
    response = client.get('/')
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_api_docs(
        client
):
    response = client.get('/docs')
    assert response.status_code == 200

# region scenarios

@pytest.mark.asyncio
async def test_scenario_creation(
        client
):
    response = client.post('/scenario', json={
        "type": "simple_shop_floor",
        "data": {
            "label": "lorem ipsum dolor sit amet"
        }
    })

    assert response.status_code == 200
    content = response.json()
    assert 'type' in content
    assert 'data' in content
    assert content['type'] == 'simple_shop_floor'
    assert content['data']['label'] == 'lorem ipsum dolor sit amet'
    assert type(content['data']['uuid']) is str

    uuid = content['data']['uuid']

    # I retrieve it back
    response = client.get(f"/scenario/{uuid}")
    assert response.status_code == 200
    content = response.json()

    assert 'type' in content
    assert 'data' in content
    assert content['type'] == 'simple_shop_floor'
    assert content['data']['label'] == 'lorem ipsum dolor sit amet'
    assert type(content['data']['uuid']) is str
    assert uuid == content['data']['uuid']

    # Delete it
    response = client.delete(f"/scenario/{uuid}")
    assert response.status_code == 200

    # And can't retrieve it anymore
    response = client.get(f"/scenario/{uuid}")
    assert response.status_code == 404

# endregion scenarios

# region resource

@pytest.mark.asyncio
async def test_resource_creation(
        client
):
    response = client.post('/scenario', json={
        "type": "simple_shop_floor",
        "data": {
            "label": "lorem ipsum dolor sit amet"
        }
    })

    assert response.status_code == 200
    content = response.json()
    uuid_scenario = content['data']['uuid']

    # the resource list is empty
    response = client.get(f"/scenario/{uuid_scenario}/resource")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0

    # creating the resource
    response = client.post(f"/scenario/{uuid_scenario}/resource", json={
        "type": "machinery_resource",
        "data": {
            "label": "production machine",
            "machine_name": "MM01"
        }
    })
    assert response.status_code == 200
    content = response.json()
    assert content['type'] == "machinery_resource"
    uuid_machine = content['data']['uuid']
    assert type(uuid_machine) is str

    # then when I retrieve the list it actually has one element
    response = client.get(f"/scenario/{uuid_scenario}/resource")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    assert content[0]['data']['uuid'] == uuid_machine
    assert content[0]['type'] == "machinery_resource"

    # todo add edit

    # and now I delete it, simply
    response = client.delete(f"/scenario/{uuid_scenario}/resource/{uuid_machine}")
    assert response.status_code == 200

    # the scenario now has 0 resources
    response = client.get(f"/scenario/{uuid_scenario}/resource")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0


# endregion resource