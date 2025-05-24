from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime

app = FastAPI()

# Order Model
class Order(BaseModel):
    customer_name: str
    items: Dict[str, float]
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

# In-memory order store
orders = {}

# Create a new order
@app.post("/orders/")
def create_order(order: Order):
    order_id = str(uuid4())
    now = datetime.utcnow()
    order.created_at = now
    order.updated_at = now
    orders[order_id] = order
    return {"order_id": order_id, "message": "Order created successfully"}

# Get all orders with filtering and pagination
@app.get("/orders/")
def get_all_orders(
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10
):
    filtered_orders = [
        {"order_id": oid, **order.dict()}
        for oid, order in orders.items()
        if status is None or order.status == status
    ]
    return filtered_orders[skip : skip + limit]

# Get single order by ID
@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

# Update order status and update timestamp
@app.put("/orders/{order_id}/status")
def update_order_status(order_id: str, new_status: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    orders[order_id].status = new_status
    orders[order_id].updated_at = datetime.utcnow()
    return {"message": "Status updated", "order": orders[order_id]}

# Get summary of total orders and total value
@app.get("/summary")
def get_summary():
    total_orders = len(orders)
    total_value = sum(sum(order.items.values()) for order in orders.values())
    return {
        "total_orders": total_orders,
        "total_value": total_value
    }
@app.delete("/orders/")
def delete_all_orders():
    orders.clear()
    return {"message": "All orders deleted successfully"}

