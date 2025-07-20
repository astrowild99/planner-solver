from dependency_injector import containers, providers
from planner_solver.config.models import TimeConfig
from planner_solver.services.time_service import TimeService

class ApplicationContainer(containers.DeclarativeContainer):
    
    config = providers.Configuration()

    # region config

    time_config = providers.Singleton(TimeConfig)

    # endregion config

    # region services

    time_service = providers.Singleton(
        TimeService,
        config=time_config
    )

    # endregion services