import asyncio
import json
import logging
from typing import Callable, List
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

logger = logging.getLogger(__name__)

class KafkaInterface:
    def __init__(self, kafka_url: str, consume_topics: List[str], message_handler: Callable):
        self._kafka_url: str = kafka_url
        self._consume_topics: List[str] = consume_topics
        self._message_handler: Callable = message_handler
        self._producer: AIOKafkaProducer = None
        self._consumer: AIOKafkaConsumer = None
        self._consumer_task: asyncio.Task = None

    async def start(self):
        logger.info("Initializing Kafka producer...")
        self._producer = AIOKafkaProducer(bootstrap_servers=self._kafka_url)
        await self._producer.start()
        logger.info("Kafka producer started")

        logger.info(f"Initizlizing Kafka consumer for topics: {self._consume_topics}")
        self._consumer = AIOKafkaConsumer(
            *self._consume_topics,
            bootstrap_servers=self._kafka_url,
            group_id="users-auth-service"
        )
        await self._consumer.start()
        logger.info("Kafka consumer started")

        self._consumer_task = asyncio.create_task(self._consume())

    async def stop(self):
        if self._producer:
            logger.info("Stopping Kafka producer...")
            await self._producer.stop()
        if self._consumer_task:
            logger.info("Stopping Kafka consumer task...")
            self._consumer_task.cancel()
        if self._consumer:
            logger.info("Stopping Kafka consumer...")
            await self._consumer.stop()

    async def send_event(self, topic: str, event: dict):
        try:
            event_bytes = json.dumps(event).encode("utf-8")
            logger.info(f"Sending event to topic: '{topic}': {event}")
            await self._producer.send_and_wait(topic, event_bytes)
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}", exc_info=True)

    async def _consume(self):
        try:
            async for msg in self._consumer:
                try:
                    event = json.loads(msg.value.decode("utf-8"))
                    logger.info(f"Received event from topic: '{msg.topic}': {event}")
                    await self._message_handler(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode event: {e}", exc_info=True)
                except Exception as e:
                    logger.error(f"Failed to handle event: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to consume events: {e}", exc_info=True)
        finally:
            logger.info("Consumer loop stopped")