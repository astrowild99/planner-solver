from typing import List
import uuid

from planner_solver.decorators.task_type import TaskType, TaskParameter
from planner_solver.models.base_models import Task, Resource, Constraint, TaskStatus, CpSatTask
from planner_solver.services.worker_service import WrappedModel


@TaskType(type_name="fixed_duration_task")
class FixedDurationTask(Task):
    label = TaskParameter(
        param_type=str
    )
    duration = TaskParameter(
        param_type=int
    )

    __uuid: str

    def __init__(self):
        super().__init__()
        self.__constraints: List[Constraint] = []
        self.__resources: List[Resource] = []
        self.__uuid: str = str(uuid.uuid4())

    def get_unique_id(self) -> str:
        return self.__uuid

    def get_duration(self) -> int:
        return self.duration

    def get_max_duration(self) -> int:
        return self.duration

    def get_constraints(self) -> List[Constraint]:
        return self.__constraints

    def add_constraint(self, constraint: Constraint) -> None:
        self.__constraints.append(constraint)

    def get_resources(self) -> List[Resource]:
        return self.__resources

    def add_resource(self, resource: Resource) -> None:
        self.__resources.append(resource)

    def generate_cp_sat(self, wrapped_model: WrappedModel, horizon: int) -> CpSatTask:
        wrapped_model.variables[f"{self.get_unique_id()}_start"] = (
            wrapped_model.model.new_int_var(0, horizon, f"{self.get_unique_id()}_start"))
        wrapped_model.variables[f"{self.get_unique_id()}_end"] = (
            wrapped_model.model.new_int_var(0, horizon, f"{self.get_unique_id()}_end"))
        wrapped_model.variables[f"{self.get_unique_id()}_interval"] = (
            wrapped_model.model.new_interval_var(
                wrapped_model.variables[f"{self.get_unique_id()}_start"],
                self.duration,
                wrapped_model.variables[f"{self.get_unique_id()}_end"],
                f"{self.get_unique_id()}_interval"
            )
        )

        self.cp_sat = CpSatTask(
            start=wrapped_model.variables[f"{self.get_unique_id()}_start"],
            end=wrapped_model.variables[f"{self.get_unique_id()}_end"],
            interval=wrapped_model.variables[f"{self.get_unique_id()}_interval"],
        )

        return self.cp_sat