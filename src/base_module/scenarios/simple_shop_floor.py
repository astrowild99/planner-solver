from typing import List

from planner_solver.decorators.scenario_type import ScenarioType
from planner_solver.models.base_models import Scenario, Task, Constraint, Resource

@ScenarioType(type_name="simple_shop_floor")
class SimpleShopFloorScenario(Scenario):
    """
    In this simple scenario, only tasks, constraints and resources are set
    """
    __tasks: List[Task]
    __constraints: List[Constraint]
    __resources: List[Resource]

    def __init__(self):
        super().__init__()
        self.__tasks = []
        self.__constraints = []
        self.__resources = []

    def get_tasks(self) -> List[Task]:
        return self.__tasks

    def add_task(self, task: Task) -> None:
        self.__tasks.append(task)

    def get_constraints(self) -> List[Constraint]:
        return self.__constraints

    def add_constraint(self, constraint: Constraint):
        self.__constraints.append(constraint)

    def get_resources(self) -> List[Resource]:
        return self.__resources

    def add_resource(self, resource: Resource):
        self.__resources.append(resource)
