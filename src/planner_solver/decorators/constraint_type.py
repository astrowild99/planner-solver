from typing import Type, Literal, List

from planner_solver.containers.singletons import types_service
from planner_solver.decorators.parameters import Parameter


class ConstraintType:
    """
    Decorates a class as a constraint
    todo define whether or not such class is a task or scenario constraint
    """
    def __init__(
            self,
            type_name: str,
            attachable_to: List[Literal['task', 'scenario']],
    ):
        self.type_name = type_name
        self.attachable_to: List[Literal['task', 'scenario']]
        """Defines the type of constraint type, whether it can be linked to a task or scenario (or both)"""

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'constraint')

        types_service.register_constraint_type(cls, self.type_name)

        return cls

class ConstraintParameter(Parameter):
    """
    the parameters added to the constraint definition
    """
    def __init__(
            self,
            param_type,
            extra_name: str | None = None,
    ):
        super().__init__(param_type, extra_name)