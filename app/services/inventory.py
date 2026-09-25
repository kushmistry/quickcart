import logging

logger = logging.getLogger(__name__)

def process_inventory(order_id: int, item: str, quantity: int) -> None:
    # Simulates reserving inventory / reducing stock in a warehouse database
    logger.info(f"[Inventory] Reduced stock for item '{item}' by {quantity} (Order #{order_id})")