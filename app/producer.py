import json
import logging
from confluent_kafka import Producer
from app.settings import settings

logger = logging.getLogger(__name__)

# Kafka Producer Configuration
conf = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "client.id": "quickcart-api-producer",
    "acks": "all",  # Wait for broker confirmation for maximum reliability
}

producer = Producer(conf)

def delivery_report(err, msg):
    """Callback executed when Kafka broker confirms or rejects the message."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(
            f"Event published to topic '{msg.topic()}' [partition {msg.partition()}] at offset {msg.offset()}"
        )

def send_order_event(order_data: dict) -> None:
    """Publishes an order_created event to Kafka."""
    # Convert order dictionary to JSON bytes
    payload = json.dumps(order_data).encode("utf-8")
    
    # Use order ID as the Kafka message key (ensures all events for an order hit the same partition)
    key = str(order_data.get("id")).encode("utf-8")

    try:
        # Asynchronously produce message to the topic
        producer.produce(
            topic=settings.KAFKA_TOPIC_ORDERS,
            key=key,
            value=payload,
            callback=delivery_report
        )
        # Serve delivery callbacks from previous requests without blocking
        producer.poll(0)
    except Exception as e:
        logger.error(f"Failed to produce message to Kafka: {e}")
        raise e

def flush_producer():
    """Flushes any remaining messages in the producer queue before shutdown."""
    producer.flush(timeout=5.0)