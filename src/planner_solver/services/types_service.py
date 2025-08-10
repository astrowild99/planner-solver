import logging
from typing import Type, List

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
        logger.info("Service loaded")

    def register_task_type(self, task: Type) -> None:
        """
        registers a new task type, via the @Type annotation
        """
        self.__task_types.append(task)
        logger.debug("Added new task type " + str(task))

    def register_resource_type(self, resource: Type) -> None:
        """
        registers a new resource type, via the @Resource annotation
        """
        self.__resource_types.append(resource)
        logger.debug("Added new resource type " + str(resource))

    def register_constraint_type(self, constraint: Type) -> None:
        """
        registers a new constraint type, via the @Constraint annotation
        """
        self.__constraint_types.append(constraint)
        logger.debug("Added new constraint type " + str(constraint))