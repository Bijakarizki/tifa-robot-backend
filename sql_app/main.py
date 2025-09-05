from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import dari file-file lokal Anda
from . import crud, models, schemas
from .database import engine, get_db

# Baris ini akan membuat tabel di database Supabase Anda
# jika belum ada, berdasarkan definisi di models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TIFA Robot Control API",
    description="API untuk mengelola pesanan dan meja untuk robot TIFA (Versi Supabase).",
    version="3.0.0",
)

# Pengaturan CORS untuk mengizinkan semua origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TIFA Robot Control API (Supabase Version)", "status": "running"}


# === API Meja (Tables) ===

@app.post("/tables/", response_model=schemas.TableResponse, tags=["Tables"])
def create_table(table: schemas.TableCreate, db: Session = Depends(get_db)):
    """
    Endpoint untuk membuat meja baru.
    Akan mengecek apakah nomor meja sudah ada sebelum membuat.
    """
    db_table = crud.get_table_by_name(db, table_name=table.table_number)
    if db_table:
        raise HTTPException(status_code=400, detail="Table with this number already exists")
    return crud.create_table(db=db, table=table)

@app.get("/tables/", response_model=List[schemas.TableResponse], tags=["Tables"])
def read_tables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil daftar semua meja.
    """
    tables = crud.get_tables(db, skip=skip, limit=limit)
    return tables

@app.get("/tables/{table_id}", response_model=schemas.TableResponse, tags=["Tables"])
def read_table(table_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil detail satu meja berdasarkan ID.
    """
    db_table = crud.get_table(db, table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@app.delete("/tables/{table_id}", tags=["Tables"])
def delete_table(table_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk menghapus meja berdasarkan ID.
    """
    db_table = crud.delete_table(db, table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"ok": True, "message": "Table deleted successfully"}


# === API Pesanan (Orders) ===

@app.get("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil daftar semua pesanan.
    """
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders