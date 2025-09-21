import logging
from typing import Type, List, Dict, TypeVar

from planner_solver.exceptions.type_exceptions import TypeException

logger = logging.getLogger(__name__)
class TypesService:
    """
    used to read/inflate and store all the software-specific types
    stores a static list of available types (that are the ones that the api
    interface will show to the user as possible data types) and inflates a
    read document based on its decorator

    beware! this is created before anything else, and is a singleton in the real sense
    that doesn't pass through dependency injection as decorators are simple functions/classes
    in python
    """

    def __init__(self):
        self.__task_types: List[Type] = []
        self.__resource_types: List[Type] = []
        self.__constraint_types: List[Type] = []
        self.__solver_types: List[Type] = []
        self.__scenario_types: List[Type] = []
        self.__target_types: List[Type] = []

        self.__type_registry: Dict[str, Type] = {}

        logger.info("Service loaded")

    def get(self, type_name: str | TypeVar) -> Type:
        search_type_name = str(type_name.lower())

        res = self.__type_registry.get(search_type_name)
        if res is None:
            raise TypeException(f"Unrecognized module type {search_type_name} (loaded {self.count()} types)")
        return res

    def count(self) -> int:
        return len(self.__type_registry)

    def register_task_type(self, task: Type, type_name: str) -> None:
        """
        registers a new task type, via the @Type annotation
        """
        self.__task_types.append(task)
        self.__type_registry[type_name.lower()] = task
        logger.debug("Added new task type " + str(task))

    def register_resource_type(self, resource: Type, type_name: str) -> None:
        """
        registers a new resource type, via the @Resource annotation
        """
        self.__resource_types.append(resource)
        self.__type_registry[type_name.lower()] = resource
        logger.debug("Added new resource type " + str(resource))

    def register_constraint_type(self, constraint: Type, type_name: str) -> None:
        """
        registers a new constraint type, via the @Constraint annotation
        """
        self.__constraint_types.append(constraint)
        self.__type_registry[type_name.lower()] = constraint
        logger.debug("Added new constraint type " + str(constraint))

    def register_solver_type(self, solver: Type, type_name: str) -> None:
        """
        registers a new solver
        """
        self.__solver_types.append(solver)
        self.__type_registry[type_name.lower()] = solver
        logger.debug("Added new solver type " + str(solver))

    def register_scenario_type(self, scenario: Type, type_name: str) -> None:
        """
        registers a new scenario type
        """
        self.__scenario_types.append(scenario)
        self.__type_registry[type_name.lower()] = scenario
        logger.debug("Added new scenario type " + str(scenario))

    def register_target_type(self, target: Type, type_name: str) -> None:
        """
        registers a new target function type
        """
        self.__target_types.append(target)
        self.__type_registry[type_name.lower()] = target
        logger.debug("Added new target function type " + str(target))