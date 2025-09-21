import pytest
import os

from planner_solver.containers import ApplicationContainer

@pytest.fixture(scope="session")
async def container():
    os.chdir('/usr/src/app')
    container = ApplicationContainer()
    container.init_resources()

    await container.mongodb_service().clear_all_collections()

    return container


@pytest.mark.asyncio
async def test_db_connection(
        container
):
    cont = await container
    mongodb_service = cont.mongodb_service()

    # I verify that everything is empty on first run
    task_documents = await mongodb_service.get_all_task_documents()
    assert len(task_documents) == 0
    constraint_documents = await mongodb_service.get_all_constraint_documents()
    assert len(constraint_documents) == 0
    resource_documents = await mongodb_service.get_all_resource_documents()
    assert len(resource_documents) == 0
    scenario_documents = await mongodb_service.get_scenario_documents()
    assert len(scenario_documents) == 0