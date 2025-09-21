import json
import logging
import asyncio
from typing import Dict, Any, Callable

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

    def start_consuming_async(self, async_callback_function: Callable) -> None:
        """Start consuming messages from the execution_trigger queue with async support"""
        self._get_connection()

        def wrapper(ch, method, properties, body):
            """Wrapper to handle async message processing and acknowledgment"""
            try:
                # Parse the JSON message
                data = json.loads(body)
                logger.info(f"Received message: {data}")

                # Run the async callback in the event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(async_callback_function(data))
                finally:
                    loop.close()

                # Acknowledge the message after successful processing
                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Reject the message and don't requeue it to avoid infinite loops
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Set up the consumer
        self.__channel.basic_qos(prefetch_count=1)  # Process one message at a time
        self.__channel.basic_consume(
            queue='execution_trigger',
            on_message_callback=wrapper
        )

        logger.info("Starting to consume messages from execution_trigger queue...")
        logger.info("To stop consuming, press CTRL+C")

        try:
            self.__channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.__channel.stop_consuming()
            self.close()

    def start_consuming(self, callback_function) -> None:
        """Start consuming messages from the execution_trigger queue (sync version)"""
        self._get_connection()

        def wrapper(ch, method, properties, body):
            """Wrapper to handle message processing and acknowledgment"""
            try:
                # Parse the JSON message
                data = json.loads(body)
                logger.info(f"Received message: {data}")

                # Call the provided callback function
                callback_function(data)

                # Acknowledge the message after successful processing
                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Reject the message and don't requeue it to avoid infinite loops
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Set up the consumer
        self.__channel.basic_qos(prefetch_count=1)  # Process one message at a time
        self.__channel.basic_consume(
            queue='execution_trigger',
            on_message_callback=wrapper
        )

        logger.info("Starting to consume messages from execution_trigger queue...")
        logger.info("To stop consuming, press CTRL+C")

        try:
            self.__channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.__channel.stop_consuming()
            self.close()

    def close(self) -> None:
        """Close the connection to RabbitMQ"""
        if self.__connection and not self.__connection.is_closed:
            self.__connection.close()
            logger.debug("Closed RabbitMQ connection")

