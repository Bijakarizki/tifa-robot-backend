# main.py

from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TIFA Robot Control API (Integrated Version)",
    description="API for managing integrated orders and navigation goals for the TIFA robot.",
    version="4.0.0",
)

# (CORS middleware, dll. tetap sama) ...

@app.get("/")
def read_root():
    return {"message": "Welcome to TIFA Robot Control API v4", "status": "running"}

# === (BARU) API untuk Koordinat Meja (Master Data) ===

@app.post("/coordinates/", response_model=schemas.TableCoordinateResponse, tags=["Coordinates"])
def create_table_coordinates(coord: schemas.TableCoordinateCreate, db: Session = Depends(get_db)):
    """Endpoint untuk mendefinisikan nomor meja dan koordinatnya di awal."""
    return crud.create_table_coordinate(db=db, coord=coord)

@app.get("/coordinates/", response_model=List[schemas.TableCoordinateResponse], tags=["Coordinates"])
def read_table_coordinates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Mendapatkan semua daftar koordinat meja yang sudah terdefinisi."""
    return crud.get_table_coordinates(db, skip=skip, limit=limit)

# === (DIUBAH) API Pesanan (Orders) ===

@app.post("/orders/bulk", response_model=List[schemas.OrderResponse], tags=["Orders"])
def create_orders_bulk(bulk_data: schemas.OrderCreateBulk, db: Session = Depends(get_db)):
    # (DIUBAH) Konversi hasil dari CRUD ke skema response
    created_orders_models = crud.create_orders_bulk(db=db, orders_data=bulk_data.orders)
    return [schemas.OrderResponse.from_orm_model(order) for order in created_orders_models]

@app.get("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # (DIUBAH) Konversi hasil dari CRUD ke skema response
    orders_models = crud.get_orders(db, skip=skip, limit=limit)
    return [schemas.OrderResponse.from_orm_model(order) for order in orders_models]

@app.patch("/orders/{order_id}/status", response_model=schemas.OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_update: schemas.OrderUpdateStatus, db: Session = Depends(get_db)):
    # (DIUBAH) Konversi hasil dari CRUD ke skema response
    updated_order_model = crud.update_order_status(db, order_id=order_id, new_status=status_update.status)
    return schemas.OrderResponse.from_orm_model(updated_order_model)

# === (DIUBAH) API Navigation Goals ===

@app.get("/navigation_goals/", response_model=List[schemas.NavigationGoalResponse], tags=["Navigation Goals"])
def read_navigation_goals_by_status(
    status: str,
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    (UNTUK ROBOT) Mengambil daftar tugas navigasi berdasarkan status.
    Contoh: GET /navigation_goals/?status=ready
    """
    return crud.get_navigation_goals_by_status(db, status=status, skip=skip, limit=limit)

@app.patch("/navigation_goals/{goal_id}/status", response_model=schemas.NavigationGoalResponse, tags=["Navigation Goals"])
def update_navigation_goal_status(
    goal_id: int, 
    status_update: schemas.NavigationGoalUpdateStatus, 
    db: Session = Depends(get_db)
):
    """
    (UNTUK ROBOT) Mengubah status sebuah goal navigasi (misal: 'ready' -> 'succeeded').
    Akan otomatis mengupdate status Order yang terhubung.
    """
    return crud.update_navigation_goal_status(db, goal_id=goal_id, new_status=status_update.status)

# (ENDPOINT BARU) Endpoint khusus untuk robot mengupdate meta
@app.patch("/navigation_goals/{goal_id}/meta", response_model=schemas.NavigationGoalResponse, tags=["Navigation Goals"])
def update_navigation_goal_meta(
    goal_id: int,
    meta_update: schemas.NavigationGoalUpdateMeta,
    db: Session = Depends(get_db)
):
    """
    (UNTUK ROBOT) Mengupdate data JSON 'meta' pada sebuah goal.
    Bisa dipakai untuk menyimpan log, sensor, atau status internal robot.
    """
    return crud.update_navigation_goal_meta(db, goal_id=goal_id, meta_data=meta_update)