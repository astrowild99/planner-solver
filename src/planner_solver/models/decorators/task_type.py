from typing import Type

from planner_solver.main import types_service
from planner_solver.models.decorators.parameters import Parameter


class TaskType:
    """
    decorate a class with this to let it behave as task and directly
    init the retrieved data with this resource definition as the defined task
    """
    def __init__(self, type_name):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'task')

        types_service.register_task_type(cls)

class TaskParameter(Parameter):
    pass