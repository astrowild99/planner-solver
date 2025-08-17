from typing import List

from ortools.sat.python.cp_model import CpModel

from planner_solver.decorators.resource_type import ResourceParameter, ResourceType
from planner_solver.models.base_models import Resource, Task


@ResourceType(type_name="machinery_resource")
class MachineryResource(Resource):
    machine_name = ResourceParameter(
        param_type=str
    )

    __attached_tasks: List[Task]

    def __init__(self):
        self.__attached_tasks = []

    def prepare_resource(self, model: CpModel) -> None:
        pass

    def attach_scenario_resource(self, model: CpModel) -> None:
        task_intervals = [task.cp_sat.interval for task in self.__attached_tasks]
        model.add_no_overlap(task_intervals)

    def attach_task_resource(self, model: CpModel, task: Task):
        self.__attached_tasks.append(task)