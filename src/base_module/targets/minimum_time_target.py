from typing import List

from ortools.sat.python.cp_model import CpModel

from planner_solver.decorators.target_type import TargetType
from planner_solver.models.base_models import Target, Task

@TargetType(type_name="min_time")
class MinimumTypeTarget(Target):
    """
    Minimizes the finish time
    """
    def attach_target(
            self,
            model: CpModel,
            horizon: int,
            tasks: List[Task]
    ) -> None:
        obj_var = model.new_int_var(0, horizon, "makespan")
        model.add_max_equality(
            obj_var,
            [task.cp_sat.end for task in tasks]
        )
        model.minimize(obj_var)