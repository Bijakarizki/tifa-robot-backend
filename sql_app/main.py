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
    version="3.3.0", # Versi dinaikkan
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

# Endpoint untuk membuat pesanan secara bulk
@app.post("/orders/bulk", response_model=List[schemas.OrderResponse], tags=["Orders"])
def create_orders_bulk(bulk_data: schemas.OrderCreateBulk, db: Session = Depends(get_db)):
    """
    Endpoint untuk membuat beberapa pesanan sekaligus.
    Status pesanan akan otomatis diatur menjadi 0 (Siap Antar).
    """
    return crud.create_orders_bulk(db=db, orders=bulk_data.orders)

@app.get("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

# Endpoint untuk update status pesanan
@app.patch("/orders/{order_id}/status", response_model=schemas.OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_update: schemas.OrderUpdateStatus, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengubah status pesanan.
    Robot akan mengubah status dari 0 -> 1.
    Frontend akan mengubah status dari 1 -> 2.
    """
    return crud.update_order_status(db, order_id=order_id, new_status=status_update.status)


# === (BLOK ENDPOINT BARU UNTUK NAVIGATION GOALS) ===

@app.post("/navigation_goals/", response_model=schemas.NavigationGoalResponse, tags=["Navigation Goals"])
def create_navigation_goal(goal: schemas.NavigationGoalCreate, db: Session = Depends(get_db)):
    """
    Membuat goal navigasi baru.
    Status akan otomatis diatur ke 'queued'.
    """
    return crud.create_navigation_goal(db=db, goal=goal)

@app.get("/navigation_goals/", response_model=List[schemas.NavigationGoalResponse], tags=["Navigation Goals"])
def read_navigation_goals(
    status: str | None = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Mengambil daftar navigation goals.
    Bisa difilter berdasarkan status (queued, running, done).
    Jika tidak ada status, ambil semua.
    """
    if status:
        return crud.get_navigation_goals_by_status(db, status=status, skip=skip, limit=limit)
    return crud.get_all_navigation_goals(db, skip=skip, limit=limit)


@app.patch("/navigation_goals/{goal_id}/status", response_model=schemas.NavigationGoalResponse, tags=["Navigation Goals"])
def update_navigation_goal_status(
    goal_id: int, 
    status_update: schemas.NavigationGoalUpdateStatus, 
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk robot mengubah status goal (misal: dari queued -> running, atau running -> done).
    """
    # new_status dari Pydantic adalah objek enum penuh, kita kirimkan ke crud
    return crud.update_navigation_goal_status(db, goal_id=goal_id, new_status=status_update.status)