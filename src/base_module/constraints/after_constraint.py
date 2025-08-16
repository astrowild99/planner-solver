from ortools.sat.python.cp_model import CpModel

from planner_solver.decorators.constraint_type import ConstraintType, ConstraintParameter
from planner_solver.models.base_models import Constraint, Task


@ConstraintType(type_name="after_constraint")
class AfterConstraint(Constraint):

    task = ConstraintParameter()

    def attach_task_constraint(self, model: CpModel, task: Task):
        # todo test type safety here
        before_task: Task = self.task
        model.add(
            before_task.cp_sat.end <= task.cp_sat.start
        )

    def attach_scenario_constraint(self, model: CpModel) -> None:
        pass