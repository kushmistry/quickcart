import time
import logging

logger = logging.getLogger(__name__)

def send_order_confirmation(order_id: int, customer_name: str, item: str) -> None:
    # Artificial delay to simulate an external third-party email API (e.g. SendGrid / SMTP)
    time.sleep(1.5)
    logger.info(f"[Email] Sent confirmation email to {customer_name} for '{item}' (Order #{order_id})")