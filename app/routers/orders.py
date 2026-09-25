from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.schemas import OrderCreate, OrderResponse
from app.services import process_inventory, send_order_confirmation, track_order_sale

router = APIRouter(prefix="/orders", tags=["Orders"])

# 1. Create Order (Version A - Synchronous)
@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    # 1. Save into PostgreSQL
    new_order = Order(**order_in.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 2. Synchronous downstream calls (Version A)
    process_inventory(order_id=new_order.id, item=new_order.item, quantity=new_order.quantity)
    send_order_confirmation(order_id=new_order.id, customer_name=new_order.customer_name, item=new_order.item)
    track_order_sale(order_id=new_order.id, item=new_order.item, price=new_order.price, quantity=new_order.quantity)

    return new_order

# 2. List Orders
@router.get("", response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

# 3. Get Order by ID
@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    return order