from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import crud, schemas

app = FastAPI(
    title="TIFA Robot Control API",
    description="API untuk mengelola pesanan dan meja untuk robot TIFA (Direct API version).",
    version="2.0.0",
)

# ... (middleware tetap sama) ...
origins = ["*"] # Izinkan semua untuk testing

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to TIFA Robot Control API"}

# === API MEJA ===

# --- PERUBAHAN DI ENDPOINT INI ---
@app.post("/tables/", response_model=Dict[str, Any], tags=["Tables"])
def create_table(table: schemas.TableCreate):
    """Membuat meja baru dan mengembalikan data input sebagai konfirmasi."""
    existing_table = crud.get_table_by_name(table_name=table.table_number)
    if existing_table:
        raise HTTPException(status_code=400, detail="Table with this number already exists")
    
    # Panggil fungsi crud yang sudah diperbarui
    success = crud.create_table(table=table)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create table in database")
    
    # Kembalikan dictionary sederhana sebagai konfirmasi, Flutter akan refresh list
    return {"ok": True, "message": "Table created successfully", "data": table.dict()}

@app.get("/tables/", response_model=List[schemas.TableResponse], tags=["Tables"])
def read_tables(skip: int = 0, limit: int = 100):
    return crud.get_tables(skip=skip, limit=limit)

@app.get("/tables/{table_id}", response_model=schemas.TableResponse, tags=["Tables"])
def read_table(table_id: int):
    db_table = crud.get_table(table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@app.delete("/tables/{table_id}", tags=["Tables"])
def delete_table(table_id: int):
    db_table = crud.delete_table(table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"ok": True, "message": "Table deleted successfully"}

# === API PESANAN ===
# (Endpoint untuk pesanan tetap sama seperti sebelumnya)
@app.post("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def create_orders(orders: List[schemas.OrderCreate]):
    return crud.create_orders_bulk(orders=orders)

@app.get("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100):
    return crud.get_orders(skip=skip, limit=limit)

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse, tags=["Orders"])
def read_order(order_id: int):
    db_order = crud.get_order(order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}/status", response_model=schemas.OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_update: schemas.OrderUpdateStatus):
    db_order = crud.update_order_status(order_id=order_id, status=status_update.status)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.delete("/orders/{order_id}", tags=["Orders"])
def delete_order(order_id: int):
    db_order = crud.delete_order(order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"ok": True, "message": "Order deleted successfully"}