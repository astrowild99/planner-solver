from typing import Type

from planner_solver.containers.singletons import types_service
from planner_solver.decorators.parameters import Parameter


class ResourceType:
    """
    decorate a class with this to let it behave like a resource
    """
    def __init__(self, type_name):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'resource')

        types_service.register_resource_type(cls, self.type_name)

        return cls

class ResourceParameter(Parameter):
    """
    the parameters added to the resource definition
    """
    pass