from abc import ABC

class Parameter(ABC):
    """
    the parameters that you can add to the single
    resource type
    """
    def __init__(self, extra_name: str | None = None):
        self.name = None
        self.extra_name = extra_name
        self.private_name = None

    def __set_name__(self, owner, name):
        self.name = name
        if self.extra_name is None:
            self.extra_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, value)