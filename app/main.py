from fastapi import FastAPI
from app.routers import health_router, orders_router

app = FastAPI(
    title="QuickCart API",
    description="E-commerce order system benchmarking Sync vs Kafka architectures",
    version="1.0.0",
    swagger_ui_parameters={"displayRequestDuration": True},  
)

# Register routers
app.include_router(health_router)
app.include_router(orders_router)