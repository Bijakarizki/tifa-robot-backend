# crud.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from typing import List

# === (BARU) Fungsi untuk Tabel Koordinat ===

def create_table_coordinate(db: Session, coord: schemas.TableCoordinateCreate):
    """Membuat data koordinat meja baru di tabel master."""
    existing_coord = db.query(models.TableCoordinate).filter(models.TableCoordinate.table_number == coord.table_number).first()
    if existing_coord:
        raise HTTPException(status_code=400, detail=f"Table '{coord.table_number}' already has coordinates defined.")
    
    db_coord = models.TableCoordinate(**coord.model_dump())
    db.add(db_coord)
    db.commit()
    db.refresh(db_coord)
    return db_coord

def get_table_coordinates(db: Session, skip: int = 0, limit: int = 100):
    """Mengambil semua data koordinat meja."""
    return db.query(models.TableCoordinate).offset(skip).limit(limit).all()

# === (DIUBAH TOTAL) Fungsi untuk Pesanan (Orders) ===

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    """Mengambil daftar pesanan, diurutkan dari yang terbaru."""
    return db.query(models.Order).order_by(models.Order.id.desc()).offset(skip).limit(limit).all()

def create_orders_bulk(db: Session, orders_data: List[schemas.OrderCreate]):
    """
    Logika utama: Membuat pesanan dan navigation goal yang terhubung secara otomatis.
    """
    created_orders = []
    for order_item in orders_data:
        # 1. Cari koordinat dari tabel master
        coord = db.query(models.TableCoordinate).filter(models.TableCoordinate.table_number == order_item.table_number).first()
        if not coord:
            raise HTTPException(status_code=404, detail=f"Coordinates for table '{order_item.table_number}' not found.")
            
        # 2. Buat Order dengan status default 'queued' dan salin koordinat
        db_order = models.Order(
            table_number=order_item.table_number,
            status=schemas.OrderStatus.QUEUED.value, # Status awal
            goal_x=coord.goal_x,
            goal_y=coord.goal_y,
            goal_yaw=coord.goal_yaw
        )
        
        # 3. Buat NavigationGoal yang terhubung secara otomatis
        db_goal = models.NavigationGoal(
            order=db_order, # Ini menghubungkan keduanya
            status=db_order.status,
            goal_x=db_order.goal_x,
            goal_y=db_order.goal_y,
            goal_yaw=db_order.goal_yaw
        )
        
        db.add(db_order)
        db.add(db_goal)
        created_orders.append(db_order)

    db.commit()
    for order in created_orders:
        db.refresh(order)
    return created_orders

def update_order_status(db: Session, order_id: int, new_status: schemas.OrderStatus):
    """
    Dipakai Frontend: Mengubah status Order DAN NavigationGoal terkait.
    Contoh: Frontend mengubah status dari 'queued' -> 'ready'.
    """
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Update status di tabel Order
    db_order.status = new_status.value
    
    # Update juga status di tabel NavigationGoal yang terhubung
    if db_order.navigation_goal:
        db_order.navigation_goal.status = new_status.value
        
    db.commit()
    db.refresh(db_order)
    return db_order

# === (DIUBAH TOTAL) Fungsi untuk Navigation Goals ===

def get_navigation_goals_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    """Dipakai Robot: Mengambil daftar tugas berdasarkan status (misal: 'ready')."""
    return db.query(models.NavigationGoal).filter(models.NavigationGoal.status == status).order_by(models.NavigationGoal.created_at.asc()).offset(skip).limit(limit).all()

def update_navigation_goal_status(db: Session, goal_id: int, new_status: schemas.GoalStatus):
    """
    Dipakai Robot: Mengubah status NavigationGoal DAN Order terkait.
    Contoh: Robot mengubah status dari 'ready' -> 'succeeded'.
    """
    db_goal = db.query(models.NavigationGoal).filter(models.NavigationGoal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Navigation Goal not found")

    # Update status di tabel NavigationGoal
    db_goal.status = new_status.value

    # Update juga status di tabel Order yang terhubung
    if db_goal.order:
        db_goal.order.status = new_status.value

    db.commit()
    db.refresh(db_goal)
    return db_goal