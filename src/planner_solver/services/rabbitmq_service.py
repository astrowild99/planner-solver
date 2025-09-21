import json
import logging
from typing import Dict, Any

import pika
from planner_solver.config.models import RabbitmqConfig

logger = logging.getLogger(__name__)

class RabbitmqService:
    """
    a singleton to handle the communication with rabbitmq
    """

    def __init__(self, config: RabbitmqConfig):
        self.__config = config
        self.__connection = None
        self.__channel = None
        logger.info("service loaded")
        logger.debug("host: " + str(config.connection.host) + ":" + str(config.connection.port))

    def _get_connection(self):
        """Establish connection to RabbitMQ if not already connected"""
        if self.__connection is None or self.__connection.is_closed:
            credentials = pika.PlainCredentials(
                self.__config.connection.username,
                self.__config.connection.password
            )
            parameters = pika.ConnectionParameters(
                host=self.__config.connection.host,
                port=int(self.__config.connection.port),
                credentials=credentials
            )
            self.__connection = pika.BlockingConnection(parameters)
            self.__channel = self.__connection.channel()
            # Declare the execution_trigger queue as persistent
            self.__channel.queue_declare(queue='execution_trigger', durable=True)
            logger.debug("Connected to RabbitMQ")

    def _publish_message(self, data: Dict[str, Any]) -> None:
        """Publish a message to the execution_trigger queue"""
        body = json.dumps(data)
        self._get_connection()

        self.__channel.basic_publish(
            exchange='',
            routing_key='execution_trigger',
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        logger.debug(f"Published message to execution_trigger queue: {body}")

    def publish_execution_trigger(self, data: Dict[str, Any]) -> None:
        """Public method to publish to execution_trigger queue"""
        self._publish_message(data)

    def close(self) -> None:
        """Close the connection to RabbitMQ"""
        if self.__connection and not self.__connection.is_closed:
            self.__connection.close()
            logger.debug("Closed RabbitMQ connection")

