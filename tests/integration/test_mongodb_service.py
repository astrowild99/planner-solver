import pytest
import os

from planner_solver.containers import ApplicationContainer

@pytest.fixture(scope="session")
def container():
    os.chdir('/usr/src/app')
    container = ApplicationContainer()
    container.init_resources()

    return container


@pytest.mark.asyncio
async def test_task_storage_retrieval(
        container
):
    mongodb_service = container.mongodb_service()

    await mongodb_service.test_connect()
    assert True == True