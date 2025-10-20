# status_service/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql

app = FastAPI(title="Status Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Database connection
conn = pymysql.connect(
    host="localhost", user="root", password="", database="service_db"
)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# ✅ Model untuk menerima data status
class StatusUpdate(BaseModel):
    order_id: str
    status: str  # pending | paid | refunded

@app.post("/status/update")
def update_status(data: StatusUpdate):
    cursor.execute("SELECT * FROM order_status WHERE order_id=%s", (data.order_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE order_status SET status=%s WHERE order_id=%s",
            (data.status, data.order_id),
        )
    else:
        cursor.execute(
            "INSERT INTO order_status (order_id, status) VALUES (%s,%s)",
            (data.order_id, data.status),
        )
    conn.commit()
    return {"success": True, "order_id": data.order_id, "status": data.status}

@app.get("/status/{order_id}")
def get_status(order_id: str):
    cursor.execute("SELECT * FROM order_status WHERE order_id=%s", (order_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Status not found")
    return row

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "status_service"}
