import logging
import sys

from dependency_injector import containers, providers
from planner_solver.config.models import TimeConfig, ModuleConfig, MongodbConfig, RabbitmqConfig, LoggingConfig
from planner_solver.services.module_loader_service import ModuleLoaderService
from planner_solver.services.mongodb_service import MongodbService
from planner_solver.services.rabbitmq_service import RabbitmqService
from planner_solver.services.time_service import TimeService

def configure_logging(config: LoggingConfig) -> None:
    print("Logging level set to " + str(config.get_logger_level()))
    logging.basicConfig(
        level=config.get_logger_level(),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

class ApplicationContainer(containers.DeclarativeContainer):
    
    config = providers.Configuration()

    # region config

    logging_config = providers.Singleton(LoggingConfig)
    time_config = providers.Singleton(TimeConfig)
    module_config = providers.Singleton(ModuleConfig)
    mongodb_config = providers.Singleton(MongodbConfig)
    rabbitmq_config = providers.Singleton(RabbitmqConfig)

    # endregion config

    # region logging

    logging_setup = providers.Resource(
        configure_logging,
        config=logging_config
    )

    # endregion logging

    # region services

    time_service = providers.Singleton(
        TimeService,
        config=time_config,
    )

    mongodb_service = providers.Singleton(
        MongodbService,
        config=mongodb_config,
    )

    rabbitmq_service = providers.Singleton(
        RabbitmqService,
        config=rabbitmq_config,
    )

    module_loader_service = providers.Singleton(
        ModuleLoaderService,
        config=module_config,
    )

    # endregion services