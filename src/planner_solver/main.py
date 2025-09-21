import subprocess
import json
import logging

from planner_solver.containers.application import ApplicationContainer
from datetime import datetime

from planner_solver.services.types_service import TypesService

def run():
    container = ApplicationContainer()
    container.init_resources()

    api_config = container.api_config()

    cmd = [
        "uvicorn",
        "planner_solver.api:app",
        "--host",
        api_config.host,
        "--port",
        str(api_config.port),
        "--log-level",
        api_config.log_level,
    ]

    subprocess.run(cmd)

def runner_run():
    logger = logging.getLogger(__name__)
    container = ApplicationContainer()
    container.init_resources()

    time_service = container.time_service()
    module_loader = container.module_loader_service()
    mongodb_service = container.mongodb_service()
    rabbitmq_service = container.rabbitmq_service()
    worker_service = container.worker_service()

    module_loader.load_all()

    logger.info(f"System time: {time_service.convert(datetime.now())}")
    logger.info(f"Loaded {len(module_loader.loaded_modules)} modules")

    async def process_execution_message(data):
        """Process execution trigger messages from RabbitMQ"""
        try:
            logger.info(f"Processing execution request: {data}")

            uuid_scenario = data.get('uuid_scenario')
            uuid_execution = data.get('uuid_execution')

            if not uuid_scenario or not uuid_execution:
                logger.error("Missing required fields: uuid_scenario or uuid_execution")
                return

            logger.info(f"Starting execution {uuid_execution} for scenario {uuid_scenario}")

            # TODO: Implement the actual execution logic here

            # 1. Fetch scenario from MongoDB using scenario_uuid (async)
            # 2. Create solver and target based on message parameters
            # 3. Use worker_service to solve the scenario
            # 4. Update execution status in MongoDB (async)

            logger.info(f"Execution {uuid_execution} completed successfully")

        except Exception as e:
            logger.error(f"Error processing execution message: {e}")
            raise

    logger.info("Starting RabbitMQ consumer for execution_trigger queue...")

    # Start consuming messages with async support - this will block until interrupted
    rabbitmq_service.start_consuming_async(process_execution_message)

