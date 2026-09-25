from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, example="Alice")
    item: str = Field(..., min_length=1, example="Wireless Mouse")
    quantity: int = Field(..., gt=0, example=2)
    price: float = Field(..., gt=0.0, example=29.99)

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)