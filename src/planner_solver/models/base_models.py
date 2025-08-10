from abc import ABC, abstractmethod
from typing import List


# this file contains all the really basic classes
# that will be handled and used, and extended alongside their
# type definitions by the runner and stored to and from the
# planning tasks

class Constraint(ABC):
    """
    The constraint, as defined in the generic constraint satisfaction
    problem, is here a set that links two or more tasks (or in general, whatever element
    in this file)
    """

class Resource(ABC):
    """
    the resource identifies all the stuffs that are linked
    to the full planning event, and that have a finite quantity
    thus has to create constraints to check their availability

    e.g. a resource is the machine, the number of operators
    or the max current drain of the shop floor
    """

class Task(ABC):
    """
    The task is the single atomic value that can be planned
    by itself is not usable, as per every other type you need to
    provide a decorated type that can be manipulated
    """

    @abstractmethod
    def get_duration(self) -> int:
        """
        the duration is evaluated right before the task is turned into
        a set of solver variables
        this means that, for tasks where this duration can depend on different
        variables, you have to take into account the existence of these dependencies
        """
        pass

    @abstractmethod
    def get_constraints(self) -> List[Constraint]:
        """
        returns the task-level constraints
        this is evaluated right before the model is run, in order to create the constraints
        based on the task implementation these can either be stored or evaluated
        """
        pass

    @abstractmethod
    def add_constraint(self, constraint: Constraint) -> None:
        """
        adds a task-level constraint
        """
        pass

    @abstractmethod
    def get_resources(self) -> List[Resource]:
        """
        returns the list of task-level resources

        this is mainly used for specific non-fungible resources
        like the machine or department
        when the resource is instead used across many (e.g. the availability of operators regardless
        of their specification) will be a scenario-level resource
        """
        pass

    @abstractmethod
    def add_resource(self, resource: Resource) -> None:
        """
        adds a new task-level resource
        """
        pass
