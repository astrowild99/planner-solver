from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, Dict, List, Type, TYPE_CHECKING

import pymongo
from beanie import Document, Link
from uuid import UUID, uuid4

from pydantic import Field

from planner_solver.containers.singletons import types_service
from planner_solver.exceptions.type_exceptions import TypeException

if TYPE_CHECKING:
    from planner_solver.models.base_models import Scenario, Resource, Constraint, Task

class BasePlannerSolverDocument(Document):
    """
    used only to store and retrieve task data
    never used directly in the software, instead obtain the
    ready entity, that explodes the data

    don't forget to add every new model to mongodb_service.py set of retriever
    """
    uuid: str = Field(default_factory=lambda: str(uuid4()), alias='uuid')
    """the unique id used to retrieve entities"""
    type: str | None = Field(default=None)
    """the type defined in the decorator, used to retrieve the full object"""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    is_deleted: bool = Field(default=False)

class TaskDocument(BasePlannerSolverDocument):
    """
    the saved task entity, used only to store and retrieve task data
    never used directly in the software
    """
    label: str
    data: Dict[str, Any] = {}

    @staticmethod
    def from_base_model(base_model: Task) -> "TaskDocument":
        if not hasattr(base_model, 'label'):
            raise TypeException("You must always define a label!")
        if not hasattr(base_model, '__ps_type_name'):
            raise TypeException("Make sure to cast to a type decorated with the module type")
        return TaskDocument(
            label=base_model.label,
            type=getattr(base_model, '__ps_type_name'),
            data=base_model.model_dump()
        )

    class Settings:
        name = "ps_documents"
        indexes = [
            [
                ("uuid", pymongo.TEXT),
                ("label", pymongo.TEXT)
            ]
        ]

class ConstraintDocument(BasePlannerSolverDocument):
    """
    the saved constraint entity, used only to store and retrieve task data
    never used directly in the software
    """
    label: str
    data: Dict[str, Any] = {}

    @staticmethod
    def from_base_model(base_model: Constraint) -> "ConstraintDocument":
        if not hasattr(base_model, 'label'):
            raise TypeException("You must always define a label!")
        if not hasattr(base_model, '__ps_type_name'):
            raise TypeException("Make sure to cast to a type decorated with the module type")
        return ConstraintDocument(
            label=base_model.label,
            type=getattr(base_model, '__ps_type_name'),
            data=base_model.model_dump()
        )

    class Settings:
        name = "ps_constraints"
        indexes = [
            [
                ("uuid", pymongo.TEXT),
                ("label", pymongo.TEXT)
            ]
        ]

class ResourceDocument(BasePlannerSolverDocument):
    """
    the saved resource entity, used only to store and retrieve task data
    never used directly in the software
    """
    label: str
    data: Dict[str, Any] = {}

    @staticmethod
    def from_base_model(base_model: Resource) -> "ResourceDocument":
        if not hasattr(base_model, 'label'):
            raise TypeException("You must always define a label!")
        if not hasattr(base_model, '__ps_type_name'):
            raise TypeException("Make sure to cast to a type decorated with the module type")
        return ResourceDocument(
            label=base_model.label,
            type=getattr(base_model, '__ps_type_name'),
            data=base_model.model_dump()
        )

    class Settings:
        name = "ps_resources"
        indexes = [
            [
                ("uuid", pymongo.TEXT),
                ("label", pymongo.TEXT)
            ]
        ]

class ScenarioDocument(BasePlannerSolverDocument):
    """
    The document that lists the scenario
    Has a unique id used to identify the scenario, and is the main communication
    between the solver and the outside world
    """
    label: str

    # here the data are hard coded as links in beanie
    tasks: Optional[List[Link[TaskDocument]]] = None
    constraints: Optional[List[Link[ConstraintDocument]]] = None
    resources: Optional[List[Link[ResourceDocument]]] = None

    data: Dict[str, Any] = {}

    @staticmethod
    def from_base_model(base_model: Scenario) -> "ScenarioDocument":
        if not hasattr(base_model, 'label'):
            raise TypeException("You must always define a label!")
        if not hasattr(base_model, '__ps_type_name'):
            raise TypeException("Make sure to cast to a type decorated with the module type")
        return ScenarioDocument(
            label=base_model.label,
            type=getattr(base_model, '__ps_type_name'),
            data=base_model.model_dump()
        )

    def to_base_model(self) -> Scenario:
        type: Type[Scenario] = types_service.get(self.type)

        data = self.data | { "uuid": self.uuid }

        return type.model_validate(data)

    class Settings:
        name = "ps_scenarios"
        indexes = [
            [
                ("uuid", pymongo.TEXT),
                ("label", pymongo.TEXT)
            ]
        ]
