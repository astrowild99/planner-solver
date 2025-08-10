from planner_solver.models.decorators.constraint import Constraint, ConstraintParameter


@Constraint(type_name="after_constraint")
class AfterConstraint:
    task = ConstraintParameter()