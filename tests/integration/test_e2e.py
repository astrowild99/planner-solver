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

# region basic scenario contents

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


@pytest.mark.asyncio
async def test_task_creation(
        client
):
    # as usual, I create a scenario
    response = client.post('/scenario', json={
        "type": "simple_shop_floor",
        "data": {
            "label": "lorem ipsum dolor sit amet"
        }
    })

    assert response.status_code == 200
    content = response.json()
    uuid_scenario = content['data']['uuid']

    # the task list should be empty
    response = client.get(f"/scenario/{uuid_scenario}/task")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0

    # now I create the task, and since I specified no resources that need
    # extra values in the task, the scenario should be ok
    # todo add scenario current status evaluation

    response = client.post(f"/scenario/{uuid_scenario}/task", json={
        "type": "fixed_duration_task",
        "data": {
            "label": "First Task",
            "duration": 2
        }
    })
    assert response.status_code == 200
    content = response.json()
    assert content['type'] == 'fixed_duration_task'
    uuid_first_task = content['data']['uuid']
    assert type(uuid_first_task) is str

    # now the list obviously has 1 item
    response = client.get(f"/scenario/{uuid_scenario}/task")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1

    # todo implement edit

    # now I delete it
    response = client.delete(f"/scenario/{uuid_scenario}/task/{uuid_first_task}")
    assert response.status_code == 200

    response = client.get(f"/scenario/{uuid_scenario}/task")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0

@pytest.mark.asyncio
async def test_constraint_linked_to_tasks_creation(
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

    # Then I append 3 tasks to the scenario,
    # one with no constraint
    # the second with the after constraint specified on the scenario_leve
    # and the third with the after constraint attached to the task itself

    response = client.post(f"/scenario/{uuid_scenario}/task", json={
        "type": "fixed_duration_task",
        "data": {
            "label": "First Task",
            "duration": 2
        }
    })
    assert response.status_code == 200
    content = response.json()
    assert content['type'] == 'fixed_duration_task'
    uuid_first_task = content['data']['uuid']
    assert type(uuid_first_task) is str

    # then a second one, whose constraint is added to the scenario
    response = client.post(f"/scenario/{uuid_scenario}/task", json={
        "type": "fixed_duration_task",
        "data": {
            "label": "Second Task",
            "duration": 3
        }
    })
    assert response.status_code == 200
    content = response.json()
    assert content['type'] == 'fixed_duration_task'
    uuid_second_task = content['data']['uuid']
    assert type(uuid_second_task) is str

    # now when I look at the constraints on the scenario level, I don't
    # find any

    response = client.get(f"/scenario/{uuid_scenario}/constraint")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0

    # I create the constraint
    response = client.post(f"/scenario/{uuid_scenario}/constraint", json={
        "type": "after_constraint_scenario",
        "data": {
            "label": "task 2 after task 1",
            "task_before": uuid_first_task,
            "task_after": uuid_second_task
        }
    })
    assert response.status_code == 200
    content = response.json()
    uuid_constraint_of_scenario = content['data']['uuid']
    assert type(uuid_constraint_of_scenario) is str

    # and I can get the constraint back
    response = client.get(f"/scenario/{uuid_scenario}/constraint")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    constraint = content[0]
    assert constraint['type'] == 'after_constraint_scenario'
    assert constraint['data']['uuid'] == uuid_constraint_of_scenario

    # and now I check that the relationship worked, and when getting back I have the full form
    task_before = constraint['data']['task_before']
    assert task_before['type'] == 'fixed_duration_task'
    assert task_before['data']['uuid'] == uuid_first_task
    assert task_before['data']['label'] == 'First Task'

    task_after = constraint['data']['task_after']
    assert task_after['type'] == 'fixed_duration_task'
    assert task_after['data']['uuid'] == uuid_second_task
    assert task_after['data']['label'] == 'Second Task'

    # and now I create a third task, with the constraint after task 2
    # response = client.post(f"/scenario/{uuid_scenario}/task", json={
    #     "type": "fixed_duration_task",
    #     "data": {
    #         "label": "Third Task",
    #         "duration": 4,
    #         "constraint"
    #     }
    # })
    # todo handle the deletion

# endregion basic scenario contents
