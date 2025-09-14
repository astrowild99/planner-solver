import asyncio
import logging
from typing import List, Optional, Union, get_type_hints

from beanie import init_beanie, Link
from beanie.exceptions import DocumentNotFound
from pymongo import AsyncMongoClient

from planner_solver.config.models import MongodbConfig
from planner_solver.models.base_models import Scenario, Resource, Task, Constraint
from planner_solver.models.stored_documents import TaskDocument, ConstraintDocument, ResourceDocument, ScenarioDocument
from planner_solver.services.types_service import TypesService
from planner_solver.decorators.parameters import Parameter

logger = logging.getLogger(__name__)

MODELS = [
    TaskDocument,
    ConstraintDocument,
    ResourceDocument,
    ScenarioDocument,
]

class MongoConnectionFactory:
    def __init__(self):
        self._clients = {}
        self._beanie_initialized_loops = set()

    async def get_client_and_init_beanie(self, connection_config):
        loop = asyncio.get_running_loop()
        loop_id = id(loop)

        # Create client if it doesn't exist for this loop
        if loop_id not in self._clients:
            client = AsyncMongoClient(
                f"mongodb://{connection_config.username}:{connection_config.password}@{connection_config.host}:{connection_config.port}",
            )
            self._clients[loop_id] = client
        else:
            client = self._clients[loop_id]

        # Initialize Beanie if not done for this loop
        if loop_id not in self._beanie_initialized_loops:
            await init_beanie(
                database=client.get_database(name=connection_config.database),
                document_models=MODELS,
            )
            self._beanie_initialized_loops.add(loop_id)

        return client

    def close_all(self):
        for client in self._clients.values():
            client.close()
        self._clients.clear()
        self._beanie_initialized_loops.clear()


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
        self.__beanie_initialized = False
        self.__connection_factory = MongoConnectionFactory()
        logger.info("service loaded")
        logger.debug("host: " + str(config.connection.host) + ":" + str(config.connection.port))

    async def __connect(self):
        client = await self.__connection_factory.get_client_and_init_beanie(
            self.__connection
        )
        return client  # Return client if you need it elsewhere

    async def clear_all_collections(self):
        await self.__connect()

        for x in MODELS:
            await x.delete_all()

    async def hydrate_parameter_links(
            self,
            base_model: Union[Task, Constraint, Resource, Scenario],
            uuid_scenario: Optional[str] = None
    ) -> Union[Task, Constraint, Resource, Scenario]:
        """
        Hydrates Parameter links in a base model by fetching referenced documents from MongoDB.

        Args:
            base_model: The model to hydrate
            uuid_scenario: Scenario UUID for scoped lookups (optional)

        Returns:
            The same model with Parameter links resolved to actual objects
        """
        await self.__connect()

        # Get all Parameter attributes from the model class
        for attr_name in dir(base_model.__class__):
            attr = getattr(base_model.__class__, attr_name)

            if isinstance(attr, Parameter):
                # Get the current value (should be a UUID string or None)
                current_value = getattr(base_model, attr_name)

                if current_value is None:
                    continue

                # If it's already hydrated (an object, not a string), skip
                if not isinstance(current_value, str):
                    continue

                # Determine what type of document to fetch based on param_type
                hydrated_value = await self._resolve_parameter_reference(
                    current_value,
                    attr.param_type,
                    uuid_scenario
                )

                if hydrated_value:
                    setattr(base_model, attr_name, hydrated_value)

        return base_model

    async def _resolve_parameter_reference(
            self,
            uuid_value: str,
            param_type: type,
            uuid_scenario: Optional[str] = None
    ) -> Optional[Union[Task, Constraint, Resource, Scenario]]:
        """
        Resolves a single parameter reference by UUID.

        Args:
            uuid_value: UUID string to resolve
            param_type: Expected type of the referenced object
            uuid_scenario: Scenario UUID for scoped lookups (optional)

        Returns:
            The resolved object or None if not found
        """
        try:
            # Determine which document type to query based on param_type
            if issubclass(param_type, Task):
                if uuid_scenario:
                    doc = await self.get_task_document(uuid_scenario, uuid_value)
                else:
                    # Fallback: search all task documents
                    doc = await TaskDocument.find(TaskDocument.uuid == uuid_value).first_or_none()
                return doc.to_base_model() if doc else None

            elif issubclass(param_type, Constraint):
                if uuid_scenario:
                    doc = await self.get_constraint_document(uuid_scenario, uuid_value)
                else:
                    doc = await self.get_constraint_document_by_uuid(uuid_value)
                return doc.to_base_model() if doc else None

            elif issubclass(param_type, Resource):
                if uuid_scenario:
                    doc = await self.get_resource_document(uuid_scenario, uuid_value)
                else:
                    # Fallback: search all resource documents
                    doc = await ResourceDocument.find(ResourceDocument.uuid == uuid_value).first_or_none()
                return doc.to_base_model() if doc else None

            elif issubclass(param_type, Scenario):
                doc = await self.get_scenario_document(uuid_value)
                return doc.to_base_model() if doc else None

        except Exception as e:
            logger.warning(f"Failed to resolve parameter reference {uuid_value} of type {param_type}: {e}")

        return None

    # region task

    async def get_all_task_documents(self) -> List[TaskDocument]:
        await self.__connect()
        return await TaskDocument.find_all().to_list()

    async def get_task_documents(
            self,
            uuid_scenario: str,
    ) -> List[TaskDocument]:
        await self.__connect()

        return await TaskDocument.find(
            ResourceDocument.scenario.uuid == uuid_scenario,
            fetch_links=True
        ).to_list()

    async def get_task_document(
            self,
            uuid_scenario: str,
            uuid: str
    ) -> TaskDocument | None:
        await self.__connect()

        return await TaskDocument.find(
            TaskDocument.scenario.uuid == uuid_scenario,
            TaskDocument.uuid == uuid,
            fetch_links=True
        ).first_or_none()

    async def store_task_document(
            self,
            uuid_scenario: str,
            task: Task,
            uuid: Optional[str] = None
    ) -> TaskDocument:
        await self.__connect()

        scenario = await self.get_scenario_document(uuid=uuid_scenario)

        if uuid is not None:
            raise Exception("Update not yet implemented")
        else:
            task_document = TaskDocument.from_base_model(task)
            task_document.scenario = scenario

            stored_task = await task_document.insert()

        task.uuid = stored_task.uuid

        return stored_task

    async def delete_task_document(
            self,
            uuid_scenario: str,
            uuid: str,
    ) -> None:
        await self.__connect()

        await TaskDocument.find(
            TaskDocument.uuid == uuid,
            TaskDocument.scenario.uuid == uuid_scenario,
            fetch_links=True
        ).delete()

    # endregion task

    # region constraint

    async def get_all_constraint_documents(
            self
    ) -> List[ConstraintDocument]:
        await self.__connect()
        return await ConstraintDocument.find_all().to_list()

    async def get_constraint_documents(
            self,
            uuid_scenario: str,
    ) -> List[ConstraintDocument]:
        await self.__connect()

        return await ConstraintDocument.find(
            ConstraintDocument.scenario.uuid == uuid_scenario,
            fetch_links=True,
        ).to_list()

    async def get_constraint_document(
            self,
            uuid_scenario: str,
            uuid: str
    ) -> ConstraintDocument | None:
        await self.__connect()
        return await ConstraintDocument.find(
            ConstraintDocument.uuid == uuid,
            ConstraintDocument.scenario.uuid == uuid_scenario,
            fetch_links=True
        ).first_or_none()

    async def store_constraint_document(
            self,
            uuid_scenario: str,
            constraint: Constraint,
            uuid: Optional[str] = None
    ) -> ConstraintDocument:
        await self.__connect()

        scenario = await self.get_scenario_document(uuid=uuid_scenario)

        if uuid is not None:
            raise Exception("Update not yet implemented")
        else:
            constraint_document = ConstraintDocument.from_base_model(constraint)
            constraint_document.scenario = scenario

            stored_constraint = await constraint_document.insert()

        constraint.uuid = stored_constraint.uuid

        return stored_constraint

    async def delete_constraint_document(
            self,
            uuid_scenario: str,
            uuid: str,
    ) -> None:
        await self.__connect()

        await ConstraintDocument.find(
            ConstraintDocument.uuid == uuid,
            ConstraintDocument.scenario.uuid == uuid_scenario,
            fetch_links=True
        ).delete()

    async def get_constraint_document_by_uuid(self, uuid: str) -> ConstraintDocument | None:
        """Get constraint document by UUID only (without scenario filtering)"""
        await self.__connect()
        return await ConstraintDocument.find(
            ConstraintDocument.uuid == uuid,
            fetch_links=True
        ).first_or_none()

    # endregion constraint

    # region resource

    async def get_all_resource_documents(
            self,
    ) -> List[ResourceDocument]:
        await self.__connect()

        return await ResourceDocument.find_all().to_list()

    async def get_resource_documents(
            self,
            uuid_scenario: str,
    ) -> List[ResourceDocument]:
        await self.__connect()

        return await ResourceDocument.find(
            ResourceDocument.scenario.uuid == uuid_scenario,
            fetch_links=True
        ).to_list()

    async def get_resource_document(
            self,
            uuid_scenario: str,
            uuid: str
    ) -> ResourceDocument | None:
        await self.__connect()

        return await ResourceDocument.find(
            ResourceDocument.scenario.uuid == uuid_scenario,
            ResourceDocument.uuid == uuid,
            fetch_links=True
        ).first_or_none()

    async def store_resource_document(
            self,
            uuid_scenario: str,
            resource: Resource,
            uuid: Optional[str] = None
    ) -> ResourceDocument:
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

    async def delete_resource_document(
            self,
            uuid_scenario,
            uuid,
    ) -> None:
        await self.__connect()

        await ResourceDocument.find(
            ResourceDocument.scenario.uuid == uuid_scenario,
            ResourceDocument.uuid == uuid,
            fetch_links=True,
        ).delete()

    # endregion resource

    # region scenario

    async def get_all_scenario_documents(self) -> List[ScenarioDocument]:
        await self.__connect()
        return await ScenarioDocument.find_all().to_list()

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
