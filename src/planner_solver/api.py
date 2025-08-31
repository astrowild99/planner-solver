"""
This creates the asgi service using FastAPI to communicate with the outside world

the apis are not the only way that the system communicates, as you can also listen to
messages exchanged via the rabbitmq server
"""
import dataclasses
import datetime

from fastapi import FastAPI

from planner_solver.containers import ApplicationContainer
from planner_solver.models.base_models import Scenario
from planner_solver.models.stored_documents import ScenarioDocument
from planner_solver.services.mongodb_service import MongodbService

app = FastAPI()

container = ApplicationContainer()
container.wire(modules=[__name__])

# region types

@dataclasses.dataclass
class HealthCheckResponse:
    status: str
    server_time: str

# endregion types

# region status

@app.get('/')
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status='[OK]',
        server_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

# endregion status

# region scenario

@app.get('/scenario/<uuid_scenario>')
async def get_scenario(
        uuid_scenario: str
):
    pass

@app.post('/scenario/')
async def post_scenario(
        scenario_form: Scenario,
        mongodb_service: MongodbService
) -> Scenario:
    """
    creates the scenario
    """
    scenario = scenario_form
    document = ScenarioDocument(
        label=''
    )


@app.put('/scenario/<uuid_scenario>')
async def put_scenario(
        uuid_scenario: str
):
    pass

@app.delete('/scenario/<uuid_scenario>')
async def delete_scenario(
        uuid_scenario: str
):
    pass

# endregion scenario