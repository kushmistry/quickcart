import json
import logging
from confluent_kafka import Consumer, KafkaError
from app.settings import settings
from app.services.email import send_order_confirmation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EMAIL] %(message)s")
logger = logging.getLogger("email_consumer")

conf = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "email-group",           # Dedicated consumer group
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
}

consumer = Consumer(conf)
consumer.subscribe([settings.KAFKA_TOPIC_ORDERS])

logger.info("Email Consumer started. Listening for order events...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            logger.error(f"Consumer error: {msg.error()}")
            break

        order_data = json.loads(msg.value().decode("utf-8"))
        logger.info(f"Received Order #{order_data['id']} (will process email in background)")

        send_order_confirmation(
            order_id=order_data["id"],
            customer_name=order_data["customer_name"],
            item=order_data["item"]
        )

except KeyboardInterrupt:
    logger.info("Stopping Email Consumer...")
finally:
    consumer.close()