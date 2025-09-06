"""
This creates the asgi service using FastAPI to communicate with the outside world

the apis are not the only way that the system communicates, as you can also listen to
messages exchanged via the rabbitmq server
"""
import dataclasses
import datetime
import json
import logging
from typing import cast

from dependency_injector.wiring import inject
from fastapi import FastAPI

from planner_solver.containers import ApplicationContainer
from planner_solver.models.base_models import Scenario
from planner_solver.models.forms import BasePlannerSolverForm

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PlannerSolver",
    description="A wrapper around google or tools to handle planning in a modular way"
)

# region services

container = ApplicationContainer()
container.init_resources()
container.wire(modules=[__name__])

time_service = container.time_service()
module_loader = container.module_loader_service()
mongodb_service = container.mongodb_service()
rabbitmq_service = container.rabbitmq_service()

api_config = container.api_config()

module_loader.load_all()

print(time_service.convert(datetime.datetime.now()))
print("Loaded " + str(len(module_loader.loaded_modules)) + " modules")

# endregion services

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

@inject
@app.post('/scenario')
async def post_scenario(
        scenario_form: BasePlannerSolverForm,
) -> BasePlannerSolverForm:
    """
    creates the scenario
    """
    scenario = cast(BasePlannerSolverForm[Scenario], scenario_form)
    logger.info(f"Created scenario with a basic data: {json.dumps(scenario_form.data)}")

    base_model = scenario_form.to_base_model()

    await mongodb_service._store_scenario_document(base_model)

    return scenario


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