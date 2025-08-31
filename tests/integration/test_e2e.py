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