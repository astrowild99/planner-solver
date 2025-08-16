from typing import Type

from planner_solver.main import types_service

class SolverType:
    """
    decorates a solver
    """

    def __init__(self, type_name):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'solver')

        types_service.register_solver_type(cls)

        return cls

