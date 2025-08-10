from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Any, Dict

import pymongo
from beanie import Document
from uuid import UUID, uuid4

from ortools.sat.python.cp_model import IntVar, IntervalVar
from pydantic import Field

# region base cp_sat

class CpSatTask:
    """
    the basic interval settings used to communicate with the or-tools
    """
    start: Optional[IntVar]
    end: Optional[IntVar]
    interval: Optional[IntervalVar]

# endregion base cp_sat


class BasePlannerSolverDocument(Document):
    """
    used only to store and retrieve task data
    never used directly in the software

    don't forget to add every new model to mongodb_service.py
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
        name = "ps_resources",
        indexes = [
            [
                ("uuid", pymongo.TEXT),
                ("label", pymongo.TEXT)
            ]
        ]