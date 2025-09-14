from typing import Optional

from ortools.sat.python.cp_model import CpModel

from planner_solver.decorators.constraint_type import ConstraintType, ConstraintParameter
from planner_solver.exceptions.type_exceptions import ConstraintAttachTypeException
from planner_solver.models.base_models import Constraint, Task


@ConstraintType(type_name="after_constraint", attachable_to=['task'])
class AfterConstraint(Constraint):

    task: Optional[Task | str] = ConstraintParameter(
        param_type=Task,
        link='task'
    )

    def attach_task_constraint(self, model: CpModel, task: Task):
        # todo test type safety here
        before_task: Task = self.task
        model.add(
            before_task.cp_sat.end <= task.cp_sat.start
        )

    def attach_scenario_constraint(self, model: CpModel) -> None:
        raise ConstraintAttachTypeException('after_constraint can only be attached to a task, use after_constraint_scenario')

@ConstraintType(type_name="after_constraint_scenario", attachable_to=['scenario'])
class AfterConstraintScenario(Constraint):
    """
    The scenario-wide version of the after constraint
    """

    task_before: Optional[Task | str] = ConstraintParameter(
        param_type=Task,
        link='task'
    )
    task_after: Optional[Task | str] = ConstraintParameter(
        param_type=Task,
        link='task'
    )

    def attach_task_constraint(
            self,
            model: CpModel,
            task: "Task"
    ) -> None:
        raise ConstraintAttachTypeException('after_constraint_scenario can only be attached to a scenario, use after_constraint')

    def attach_scenario_constraint(
            self,
            model: CpModel
    ) -> None:
        before_task: Task = self.task_before
        after_task: Task = self.task_after

        if not before_task or not after_task:
            raise ValueError("Cannot resolve task references for AfterConstraintScenario")

        model.add(
            before_task.cp_sat.end <= after_task.cp_sat.start
        )