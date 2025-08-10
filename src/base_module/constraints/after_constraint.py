from planner_solver.models.decorators.constraint_type import ConstraintType, ConstraintParameter


@ConstraintType(type_name="after_constraint")
class AfterConstraint:
    task = ConstraintParameter()