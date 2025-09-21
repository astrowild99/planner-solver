from typing import TypeVar, Any, Dict, Optional, Generic

from pydantic import BaseModel

from planner_solver.containers.singletons import types_service

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

    def __init__(
            self,
            **kwargs):
        super().__init__(**kwargs)

    def to_base_model(self) -> Optional[T]:
        """
        checks the content of the form and creates the model
        """
        model_type: BaseModel = types_service.get(self.type)

        print("AND THIS IS WHERE I FAIL")

        return model_type.model_validate(self.data)
