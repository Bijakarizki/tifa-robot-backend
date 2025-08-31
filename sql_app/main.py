from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import crud, schemas

app = FastAPI(
    title="TIFA Robot Control API",
    description="API untuk mengelola pesanan dan meja untuk robot TIFA (Direct API version).",
    version="2.0.0",
)

# ... (kode middleware tetap sama) ...
origins = ["*"] # Izinkan semua untuk tes

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
@app.post("/tables/", response_model=schemas.TableCreate, tags=["Tables"])
def create_table(table: schemas.TableCreate):
    # Kita modifikasi ini agar tidak bergantung pada database
    print(f"Menerima data meja baru: {table.table_number}")
    return table

@app.get("/tables/", response_model=List[schemas.TableResponse], tags=["Tables"])
def read_tables(skip: int = 0, limit: int = 100):
    # --- PERUBAHAN UTAMA DI SINI ---
    # Kita tidak memanggil database sama sekali.
    # Kita paksa endpoint ini untuk mengembalikan data palsu.
    print("Mengembalikan data meja palsu (hardcoded) untuk tes.")
    fake_data = [
        {"id": 998, "table_number": "DATA-PALSU-1", "coordinates": "123,456"},
        {"id": 999, "table_number": "DATA-BERHASIL-TERLIHAT", "coordinates": "789,012"}
    ]
    return fake_data
    # Baris asli kita nonaktifkan sementara
    # return crud.get_tables(skip=skip, limit=limit)


# Endpoint lain bisa dibiarkan apa adanya untuk saat ini
@app.get("/tables/{table_id}", response_model=schemas.TableResponse, tags=["Tables"])
def read_table(table_id: int):
    # ...
    pass

@app.delete("/tables/{table_id}", tags=["Tables"])
def delete_table(table_id: int):
    # ...
    pass

# === API PESANAN ===
# ... (sisa kode pesanan tetap sama) ...
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