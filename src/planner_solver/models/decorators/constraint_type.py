from typing import Type

from planner_solver.main import types_service

class ConstraintType:
    def __init__(self, type_name):
        self.type_name = type_name

    def __call__(self, cls: Type):
        setattr(cls, '__ps_type_name', self.type_name)
        setattr(cls, '__ps_type_type', 'constraint')

        types_service.register_constraint_type(cls)

class ConstraintParameter:
    def __init__(self, extra_name: str | None = None):
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