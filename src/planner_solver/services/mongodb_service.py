import logging

from planner_solver.config.models import MongodbConfig

logger = logging.getLogger(__name__)

class MongodbService:
    """
    keeps the connection with mongodb
    """
    def __init__(self, config: MongodbConfig):
        self.__config = config
        logger.info("service loaded")
        logger.debug("host: " + str(config.connection.host) + ":" + str(config.connection.port))

    # todo implement this service