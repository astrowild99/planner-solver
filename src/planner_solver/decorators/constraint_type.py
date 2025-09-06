from typing import Type

from planner_solver.containers.singletons import types_service
from planner_solver.decorators.parameters import Parameter


class ConstraintType:
    """
    Decorates a class as a constraint
    todo define whether or not such class is a task or scenario constraint
    """
    def __init__(self, type_name: str):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'constraint')

        types_service.register_constraint_type(cls, self.type_name)

        return cls

class ConstraintParameter(Parameter):
    """
    the parameters added to the constraint definition
    """
    pass