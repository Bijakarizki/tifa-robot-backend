# crud.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from typing import List

# === Fungsi untuk Tabel Koordinat ===
def create_table_coordinate(db: Session, coord: schemas.TableCoordinateCreate):
    existing_coord = db.query(models.TableCoordinate).filter(models.TableCoordinate.table_number == coord.table_number).first()
    if existing_coord:
        raise HTTPException(status_code=400, detail=f"Table '{coord.table_number}' already has coordinates defined.")
    db_coord = models.TableCoordinate(**coord.model_dump())
    db.add(db_coord)
    db.commit()
    db.refresh(db_coord)
    return db_coord

def get_table_coordinates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TableCoordinate).offset(skip).limit(limit).all()

# === Fungsi untuk Pesanan (Orders) ===
def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(models.Order.id.desc()).offset(skip).limit(limit).all()

def create_orders_bulk(db: Session, orders_data: List[schemas.OrderCreate]):
    created_orders = []
    for order_item in orders_data:
        coord = db.query(models.TableCoordinate).filter(models.TableCoordinate.table_number == order_item.table_number).first()
        if not coord:
            raise HTTPException(status_code=404, detail=f"Coordinates for table '{order_item.table_number}' not found.")
        
        db_order = models.Order(
            table_number=order_item.table_number,
            status=schemas.OrderStatus.QUEUED.value,
            goal_x=coord.goal_x,
            goal_y=coord.goal_y,
            goal_yaw=coord.goal_yaw
        )
        
        db_goal = models.NavigationGoal(
            order=db_order,
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
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    db_order.status = new_status.value
    
    if db_order.navigation_goal:
        db_order.navigation_goal.status = new_status.value
        
    db.commit()
    db.refresh(db_order)
    return db_order

# === Fungsi untuk Navigation Goals ===

# (INI FUNGSI YANG HILANG)
# Fungsi ini dibutuhkan oleh fungsi di bawahnya.
def get_navigation_goal(db: Session, goal_id: int):
    """Fungsi pembantu untuk mengambil satu goal berdasarkan ID."""
    return db.query(models.NavigationGoal).filter(models.NavigationGoal.id == goal_id).first()

def get_navigation_goals_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    """Mengambil daftar tugas navigasi berdasarkan status."""
    return db.query(models.NavigationGoal).filter(models.NavigationGoal.status == status).order_by(models.NavigationGoal.created_at.asc()).offset(skip).limit(limit).all()

def update_navigation_goal_status(db: Session, goal_id: int, new_status: schemas.GoalStatus):
    """Memperbarui status navigation goal dan order terkait."""
    db_goal = get_navigation_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Navigation Goal not found")

    db_goal.status = new_status.value

    if db_goal.order:
        db_goal.order.status = new_status.value
        
    db.commit()
    db.refresh(db_goal)
    return db_goal

def update_navigation_goal_meta(db: Session, goal_id: int, meta_data: schemas.NavigationGoalUpdateMeta):
    """
    Memperbarui kolom 'meta' dari sebuah navigation goal.
    Ini bisa digunakan oleh robot untuk menyimpan log atau status internal.
    """
    # Fungsi ini memanggil get_navigation_goal()
    db_goal = get_navigation_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Navigation Goal not found")
    
    db_goal.meta = meta_data.meta
    db.commit()
    db.refresh(db_goal)
    return db_goal