import logging

logger = logging.getLogger(__name__)

def track_order_sale(order_id: int, item: str, price: float, quantity: int) -> None:
    total_amount = price * quantity
    # Simulates sending an event to an analytics platform / data warehouse
    logger.info(f"[Analytics] Logged sale: Order #{order_id} | Item: {item} | Total: ${total_amount:.2f}")