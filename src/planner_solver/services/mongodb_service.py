import logging
from typing import List, Optional

from beanie import init_beanie, Link
from beanie.exceptions import DocumentNotFound
from pymongo import AsyncMongoClient

from planner_solver.config.models import MongodbConfig
from planner_solver.models.base_models import Scenario, Resource
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
            f"mongodb://{self.__connection.username}:{self.__connection.password}@{self.__connection.host}:{self.__connection.port}",
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

    # region task

    async def get_task_documents(self) -> List[TaskDocument]:
        await self.__connect()
        return await TaskDocument.find_all().to_list()

    async def get_task_document(self, uuid: str) -> TaskDocument | None:
        await self.__connect()
        return await TaskDocument.find(
            TaskDocument.uuid == uuid
        ).first_or_none()

    # endregion task

    # region constraint

    async def get_constraint_documents(self) -> List[ConstraintDocument]:
        await self.__connect()
        return await ConstraintDocument.find_all().to_list()

    async def get_constraint_document(self, uuid: str) -> ConstraintDocument | None:
        await self.__connect()
        return await ConstraintDocument.find(
            ConstraintDocument.uuid == uuid
        ).first_or_none()

    # endregion constraint

    # region resource

    async def get_resource_documents(
            self,
            uuid_scenario: str,
    ) -> List[ResourceDocument]:
        await self.__connect()

        scenario = await self.get_scenario_document(uuid_scenario)

        if not scenario:
            return []

        return await ResourceDocument.find(
            ResourceDocument.scenario.id == scenario.id
        ).to_list()

    async def get_resource_document(
            self,
            uuid_scenario: str,
            uuid: str
    ) -> ResourceDocument | None:
        await self.__connect()

        scenario = await self.get_scenario_document(uuid_scenario)

        return await ResourceDocument.find(
            ResourceDocument.scenario == scenario,
            ResourceDocument.uuid == uuid
        ).first_or_none()

    async def store_resource_document(
            self,
            uuid_scenario,
            resource: Resource,
            uuid: Optional[str] = None
    ):
        await self.__connect()

        scenario = await self.get_scenario_document(uuid_scenario)

        if uuid is not None:
            raise Exception("Update not yet implemented")
        else:
            resource_document = ResourceDocument.from_base_model(resource)
            resource_document.scenario = scenario

            stored_resource = await resource_document.insert()

        resource.uuid = stored_resource.uuid

        return stored_resource

    # endregion resource

    # region scenario

    async def get_scenario_documents(self) -> List[ScenarioDocument]:
        await self.__connect()
        return await ScenarioDocument.find_all().to_list()

    async def get_scenario_document(self, uuid: str) -> ScenarioDocument:
        await self.__connect()
        return await ScenarioDocument.find(
            ScenarioDocument.uuid == uuid
        ).first_or_none()

    async def store_scenario_document(
            self,
            scenario: Scenario,
            uuid: Optional[str] = None
    ) -> ScenarioDocument:
        await self.__connect()
        if uuid is not None:
            stored_scenario = await self.get_scenario_document(uuid)
            raise Exception("Update not yet implemented")
            # todo handle update
        else:
            scenario_document = ScenarioDocument.from_base_model(scenario)

            stored_scenario = await scenario_document.insert()

        logger.info(f"Retrieving the uuid {str(stored_scenario.uuid)}")
        scenario.uuid = stored_scenario.uuid

        return stored_scenario

    async def delete_scenario_document(
            self,
            uuid: str,
    ):
        await self.__connect()

        found = await self.get_scenario_document(uuid)

        if not found:
            raise DocumentNotFound(f"Scenario not found for uuid {uuid}")

        await found.delete()

        return found


    # endregion scenario
