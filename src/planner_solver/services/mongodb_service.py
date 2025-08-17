import logging

from beanie import init_beanie
from pymongo import AsyncMongoClient

from planner_solver.config.models import MongodbConfig
from planner_solver.models.stored_documents import TaskDocument, ConstraintDocument, ResourceDocument, ScenarioDocument
from planner_solver.services.types_service import TypesService

logger = logging.getLogger(__name__)


class MongodbService:
    """
    keeps the connection with mongodb, retrieves all the documents
    """

    def __init__(
            self,
            config: MongodbConfig,
            types_service: TypesService,
    ):
        self.__config = config
        self.__connection = config.connection
        self.__types_service = types_service
        logger.info("service loaded")
        logger.debug("host: " + str(config.connection.host) + ":" + str(config.connection.port))

    async def __connect(self):
        client = AsyncMongoClient(
            f"mongodb://{self.__connection.username}:{self.__connection.password}@{self.__connection.host}:{self.__connection.port}"
        )

        await init_beanie(
            database=client.get_database(
                name=self.__connection.database
            ),
            document_models=[
                TaskDocument,
                ConstraintDocument,
                ResourceDocument,
                ScenarioDocument,
            ]
        )

    async def test_connect(self):
        await self.__connect()

    # region task

    async def _get_task_document(self, uuid: str) -> TaskDocument | None:
        await self.__connect()
        return await TaskDocument.find(
            TaskDocument.uuid == uuid
        ).first_or_none()

    # endregion task

    # region constraint

    async def _get_constraint_document(self, uuid: str) -> ConstraintDocument | None:
        await self.__connect()
        return await ConstraintDocument.find(
            ConstraintDocument.uuid == uuid
        ).first_or_none()

    # endregion constraint

    # region resource

    async def _get_resource_document(self, uuid: str) -> ResourceDocument | None:
        await self.__connect()
        return await ResourceDocument.find(
            ResourceDocument.uuid == uuid
        ).first_or_none()

    # endregion resource

    # region
