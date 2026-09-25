import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import health_router, orders_router
from app.producer import flush_producer

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown: ensure all buffered Kafka messages are delivered
    flush_producer()

app = FastAPI(
    title="QuickCart API",
    description="E-commerce order system benchmarking Sync vs Kafka architectures",
    version="1.0.0",
    swagger_ui_parameters={"displayRequestDuration": True},
    lifespan=lifespan
)

# Register routers
app.include_router(health_router)
app.include_router(orders_router)