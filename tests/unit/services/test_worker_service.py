import logging
import sys
from unittest.mock import MagicMock

import pytest

from base_module.constraints.after_constraint import AfterConstraint
from base_module.resources.machinery_resource import MachineryResource
from base_module.scenarios.simple_shop_floor import SimpleShopFloorScenario
from base_module.solvers.simple_solver import SimpleSolver
from base_module.targets.minimum_time_target import MinimumTypeTarget
from base_module.tasks.fixed_duration_task import FixedDurationTask
from planner_solver.config.models import ModuleConfig, MongodbConfig
from planner_solver.models.base_models import Scenario
from planner_solver.services.module_loader_service import ModuleLoaderService
from planner_solver.services.mongodb_service import MongodbService
from planner_solver.services.rabbitmq_service import RabbitmqService
from planner_solver.services.worker_service import WorkerService


@pytest.fixture
def mock_module_config():
    config = MagicMock(spec=ModuleConfig)
    config.module_paths = ['./../src/base_module']
    return config

@pytest.fixture
def mock_mongodb_service():
    return MagicMock(spec=MongodbService)

@pytest.fixture
def mock_rabbitmq_service():
    return MagicMock(spec=RabbitmqService)

@pytest.mark.asyncio
async def test_simple_worker(
        mock_module_config,
        mock_mongodb_service,
        mock_rabbitmq_service,
        caplog
):
    caplog.set_level(logging.DEBUG)

    module_loader_service = ModuleLoaderService(mock_module_config)

    # creating a very simple scenario
    # not caring about how the stuffs are retrieved
    machinery_resource = MachineryResource()
    machinery_resource.machine_name = "m1"

    # a simple couple tasks
    task_a = FixedDurationTask()
    task_a.duration = 2
    task_b = FixedDurationTask()
    task_b.duration = 3

    # a simple relation between the two
    after_constraint = AfterConstraint()
    after_constraint.task = task_b

    task_a.add_constraint(after_constraint)

    # with a fixed constraint of number of operators
    scenario = SimpleShopFloorScenario()
    scenario.add_resource(machinery_resource)
    scenario.add_task(task_a)
    scenario.add_task(task_b)

    # and my default solver
    solver = SimpleSolver()

    # and my default target
    target = MinimumTypeTarget()

    # load the worker service
    worker_service = WorkerService(
        mongodb_service=mock_mongodb_service,
        rabbitmq_service=mock_rabbitmq_service
    )

    worker_unit = worker_service.prepare_worker(scenario, solver, target)

    worker_service.solve_synchronously(worker_unit)
    # todo finish the test