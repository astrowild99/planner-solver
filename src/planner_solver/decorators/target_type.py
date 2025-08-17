from typing import Type

from planner_solver.decorators.parameters import Parameter
from planner_solver.containers.singletons import types_service


class TargetType:
    """
    decorates a target function
    """

    def __init__(self, type_name: str):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'target')

        types_service.register_target_type(cls)

        return cls

class TargetParameter(Parameter):
    pass