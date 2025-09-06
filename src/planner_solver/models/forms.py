from typing import TypeVar, Any, Dict, Optional, Generic

from pydantic import BaseModel

from planner_solver.containers.singletons import types_service
from planner_solver.exceptions.type_exceptions import TypeException
from planner_solver.models.base_models import PlannerSolverBaseModel

T = TypeVar('T')

class BasePlannerSolverForm(BaseModel, Generic[T]):
    """
    defines a form to create an entity with its relative
    type
    """
    type: str
    """the type used to pick the right module"""
    data: Dict[str, Any] | None = None
    """the dict to create the model"""

    def to_base_model(self) -> Optional[T]:
        """
        checks the content of the form and creates the model
        """
        model_type: T = types_service.get(self.type)
        # model_type() # todo actually implement them
        return None