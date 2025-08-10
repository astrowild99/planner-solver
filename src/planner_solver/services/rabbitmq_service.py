import logging

from planner_solver.config.models import RabbitmqConfig

logger = logging.getLogger(__name__)

class RabbitmqService:
    """
    a singleton to handle the communication with rabbitmq
    """

    def __init__(self, config: RabbitmqConfig):
        self.__config = config
        logger.info("[rabbitmq] - service loaded")

    # todo implement this service