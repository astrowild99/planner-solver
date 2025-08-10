from typing import Type

from planner_solver.main import types_service

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

class TaskParameter:
    """
    defines the datatype of a task so that it gets stored in extras
    and is served as is when the type definition is ready
    """
    def __init__(
            self,
            extra_name: str | None = None
    ):
        self.name = None
        self.extra_name = extra_name
        self.private_name = None

    def __set_name__(self, owner, name):
        self.name = name
        if self.extra_name == None:
            self.extra_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)