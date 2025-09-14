"""
This creates the asgi service using FastAPI to communicate with the outside world

the apis are not the only way that the system communicates, as you can also listen to
messages exchanged via the rabbitmq server
"""
import dataclasses
import datetime
import logging
from typing import cast

from fastapi import FastAPI, HTTPException

from planner_solver.containers import ApplicationContainer
from planner_solver.models.base_models import Scenario, Resource
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

@app.get('/scenario')
async def get_scenarios():
    found = await mongodb_service.get_scenario_documents()

    return [f.to_base_model().to_form() for f in found]

@app.get('/scenario/{uuid_scenario}')
async def get_scenario(
        uuid_scenario: str
):
    found = await mongodb_service.get_scenario_document(uuid_scenario)

    if not found:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return found.to_base_model().to_form()

@app.post('/scenario')
async def post_scenario(
        scenario_form: BasePlannerSolverForm,
) -> BasePlannerSolverForm[Scenario]:
    """
    creates the scenario
    """
    scenario = cast(BasePlannerSolverForm[Scenario], scenario_form)

    base_model = scenario.to_base_model()

    await mongodb_service.store_scenario_document(base_model)

    return base_model.to_form()

@app.delete('/scenario/{uuid_scenario}')
async def delete_scenario(
        uuid_scenario: str
):
    deleted = await mongodb_service.delete_scenario_document(uuid_scenario)

    return deleted.to_base_model().to_form()

# endregion scenario

# region resource

@app.get('/scenario/{uuid_scenario}/resource')
async def get_scenario_resources(
        uuid_scenario: str
):
    found = await mongodb_service.get_resource_documents(uuid_scenario=uuid_scenario)

    return [f.to_base_model().to_form() for f in found]

@app.get('/scenario/{uuid_scenario}/resource/{uuid}')
async def get_scenario_resource(
        uuid_scenario: str,
        uuid: str
):
    found = await mongodb_service.get_resource_document(
        uuid_scenario=uuid_scenario,
        uuid=uuid
    )

    if not found:
        raise HTTPException(status_code=404, detail='scenario resource not found')

    return found.to_base_model().to_form()

@app.post('/scenario/{uuid_scenario}/resource')
async def post_scenario_resource(
        uuid_scenario: str,
        resource_form: BasePlannerSolverForm,
) -> BasePlannerSolverForm[Resource]:
    scenario_document = await mongodb_service.get_scenario_document(uuid_scenario)

    if not scenario_document:
        raise HTTPException(status_code=404, detail='scenario not found')

    resource = cast(BasePlannerSolverForm[Resource], resource_form)

    base_model = resource.to_base_model()

    await mongodb_service.store_resource_document(
        uuid_scenario=uuid_scenario,
        resource=base_model
    )

    return base_model.to_form()

@app.delete('/scenario/{uuid_scenario}/resource/{uuid}')
async def delete_scenario_resource(
        uuid_scenario: str,
        uuid: str
) -> BasePlannerSolverForm[Resource]:
    scenario_document = await mongodb_service.get_scenario_document(uuid_scenario)

    if not scenario_document:
        raise HTTPException(status_code=404, detail='scenario not found')

    found = await mongodb_service.get_resource_document(
        uuid_scenario=uuid_scenario,
        uuid=uuid
    )

    if not found:
        raise HTTPException(status_code=404, detail='resource not found')

    await mongodb_service.delete_resource_document(
        uuid_scenario=uuid_scenario,
        uuid=uuid
    )

    return found.to_base_model().to_form()


# endregion resource