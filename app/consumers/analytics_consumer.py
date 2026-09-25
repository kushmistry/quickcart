import json
import logging
from confluent_kafka import Consumer, KafkaError
from app.settings import settings
from app.services.analytics import track_order_sale

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ANALYTICS] %(message)s")
logger = logging.getLogger("analytics_consumer")

conf = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "analytics-group",       # Dedicated consumer group
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
}

consumer = Consumer(conf)
consumer.subscribe([settings.KAFKA_TOPIC_ORDERS])

logger.info("Analytics Consumer started. Listening for order events...")

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
        track_order_sale(
            order_id=order_data["id"],
            item=order_data["item"],
            price=order_data["price"],
            quantity=order_data["quantity"]
        )

except KeyboardInterrupt:
    logger.info("Stopping Analytics Consumer...")
finally:
    consumer.close()