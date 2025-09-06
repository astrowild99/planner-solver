from datetime import datetime
from typing import Optional, Any, Dict, List

import pymongo
from beanie import Document, Link
from uuid import UUID, uuid4

from pydantic import Field

from planner_solver.exceptions.type_exceptions import TypeException
from planner_solver.models.base_models import Scenario


class BasePlannerSolverDocument(Document):
    """
    used only to store and retrieve task data
    never used directly in the software, instead obtain the
    ready entity, that explodes the data

    don't forget to add every new model to mongodb_service.py set of retriever
    """
    uuid: UUID = Field(default_factory=uuid4)

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
        return ScenarioDocument(
            label=base_model.label,
            data=base_model.model_dump()
        )


    class Settings:
        name = "ps_scenarios"
        indexes = [
            [
                ("uuid", pymongo.TEXT),
                ("label", pymongo.TEXT)
            ]
        ]
