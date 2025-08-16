from typing import Type

from planner_solver.main import types_service
from planner_solver.models.decorators.parameters import Parameter


class ConstraintType:
    def __init__(self, type_name):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'constraint')

        types_service.register_constraint_type(cls)

class ConstraintParameter(Parameter):
    """
    the parameters added to the constraint definition
    """
    pass