from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
import uuid

app = FastAPI(title="Entity Service")

conn = pymysql.connect(
    host="localhost", user="root", password="", database="service_db"
)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# Models
class OrderRequest(BaseModel):
    product_name: str
    price: float
    user_id: int = 1

class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    payment_type: str = "credit_card"

class RefundRequest(BaseModel):
    order_id: str
    amount: float

# Create Order
@app.post("/orders")
def create_order(req: OrderRequest):
    order_id = "ORD-" + str(uuid.uuid4())[:8]
    cursor.execute(
        "INSERT INTO orders (order_id, product_name, price, status, user_id) VALUES (%s,%s,%s,%s,%s)",
        (order_id, req.product_name, req.price, "pending", req.user_id),
    )
    conn.commit()
    return {"success": True, "order_id": order_id, "product_name": req.product_name, "price": req.price, "status": "pending"}

# Get all orders
@app.get("/orders")
def get_orders():
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    return cursor.fetchall()

# Get specific order
@app.get("/orders/{order_id}")
def get_order(order_id: str):
    cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Payment
@app.post("/payments")
def create_payment(req: PaymentRequest):
    cursor.execute("SELECT * FROM orders WHERE order_id=%s", (req.order_id,))
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order status
    cursor.execute("UPDATE orders SET status='paid' WHERE order_id=%s", (req.order_id,))
    cursor.execute(
        "INSERT INTO payments (order_id, amount, payment_type, status) VALUES (%s,%s,%s,%s)",
        (req.order_id, req.amount, req.payment_type, "paid"),
    )
    conn.commit()
    return {"success": True, "order_id": req.order_id, "status": "paid"}

# Refund
@app.post("/refunds")
def create_refund(req: RefundRequest):
    cursor.execute("SELECT * FROM orders WHERE order_id=%s", (req.order_id,))
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    cursor.execute("UPDATE orders SET status='refunded' WHERE order_id=%s", (req.order_id,))
    cursor.execute(
        "INSERT INTO refunds (order_id, amount, status) VALUES (%s,%s,%s)",
        (req.order_id, req.amount, "refunded"),
    )
    conn.commit()
    return {"success": True, "order_id": req.order_id, "status": "refunded"}

# List all payments
@app.get("/payments")
def list_payments():
    cursor.execute("SELECT * FROM payments ORDER BY created_at DESC")
    return cursor.fetchall()

# List all refunds
@app.get("/refunds")
def list_refunds():
    cursor.execute("SELECT * FROM refunds ORDER BY created_at DESC")
    return cursor.fetchall()
