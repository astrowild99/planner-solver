import logging

from planner_solver.config.models import RabbitmqConfig

logger = logging.getLogger(__name__)

class RabbitmqService:
    """
    a singleton to handle the communication with rabbitmq
    """

    def __init__(self, config: RabbitmqConfig):
        self.__config = config
        logger.info("service loaded")
        logger.debug("host: " + str(config.connection.host) + ":" + str(config.connection.port))

    # todo implement this service