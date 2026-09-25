import json
import logging
from confluent_kafka import Consumer, KafkaError
from app.settings import settings
from app.services.inventory import process_inventory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [INVENTORY] %(message)s")
logger = logging.getLogger("inventory_consumer")

conf = {
    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "inventory-group",        # Dedicated consumer group
    "auto.offset.reset": "earliest",     # Start from beginning if no offset committed
    "enable.auto.commit": True,          # Automatically commit offsets
}

consumer = Consumer(conf)
consumer.subscribe([settings.KAFKA_TOPIC_ORDERS])

logger.info("Inventory Consumer started. Listening for order events...")

try:
    while True:
        # Poll Kafka for new messages (timeout 1.0s)
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            logger.error(f"Consumer error: {msg.error()}")
            break

        # Deserialize JSON payload
        order_data = json.loads(msg.value().decode("utf-8"))
        logger.info(f"Received Order #{order_data['id']} from partition {msg.partition()} at offset {msg.offset()}")

        # Execute business logic
        process_inventory(
            order_id=order_data["id"],
            item=order_data["item"],
            quantity=order_data["quantity"]
        )

except KeyboardInterrupt:
    logger.info("Stopping Inventory Consumer...")
finally:
    consumer.close()