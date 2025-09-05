from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TIFA Robot Control API",
    description="API for managing orders and tables for the TIFA robot (Supabase Version).",
    version="3.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TIFA Robot Control API", "status": "running"}

# === API Meja (Tables) ===
@app.post("/tables/", response_model=schemas.TableResponse, tags=["Tables"])
def create_table(table: schemas.TableCreate, db: Session = Depends(get_db)):
    return crud.create_table(db=db, table=table)

@app.get("/tables/", response_model=List[schemas.TableResponse], tags=["Tables"])
def read_tables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tables(db, skip=skip, limit=limit)

# === API Pesanan (Orders) ===

@app.post("/orders/", response_model=schemas.OrderResponse, tags=["Orders"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

# (BARU) Endpoint untuk membuat pesanan secara bulk
@app.post("/orders/bulk", response_model=List[schemas.OrderResponse], tags=["Orders"])
def create_orders_bulk(bulk_data: schemas.OrderCreateBulk, db: Session = Depends(get_db)):
    """
    Endpoint untuk membuat beberapa pesanan sekaligus.
    Status pesanan akan otomatis diatur menjadi 0 (Baru).
    """
    return crud.create_orders_bulk(db=db, orders=bulk_data.orders)

@app.get("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

# (BARU) Endpoint untuk update status pesanan
@app.patch("/orders/{order_id}/status", response_model=schemas.OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_update: schemas.OrderUpdateStatus, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengubah status pesanan.
    Contoh: status=1 (Diantar), status=2 (Selesai).
    """
    return crud.update_order_status(db, order_id=order_id, new_status=status_update.status)