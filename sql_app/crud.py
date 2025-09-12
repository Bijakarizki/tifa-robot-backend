# crud.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from . import models, schemas
from typing import List

# === Fungsi untuk Tabel Koordinat (tidak ada perubahan) ===
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
def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Order]:
    # (DIUBAH) Gunakan joinedload untuk eager loading, ini lebih efisien
    # untuk mengambil navigation_goal bersamaan dengan order.
    return (
        db.query(models.Order)
        .options(joinedload(models.Order.navigation_goal))
        .order_by(models.Order.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_orders_bulk(db: Session, orders_data: List[schemas.OrderCreate]) -> List[models.Order]:
    created_orders = []
    for order_item in orders_data:
        coord = db.query(models.TableCoordinate).filter(models.TableCoordinate.table_number == order_item.table_number).first()
        if not coord:
            raise HTTPException(status_code=404, detail=f"Coordinates for table '{order_item.table_number}' not found.")
        
        # (DIUBAH) Tidak ada 'status' saat membuat Order
        db_order = models.Order(
            table_number=order_item.table_number,
            goal_x=coord.goal_x,
            goal_y=coord.goal_y,
            goal_yaw=coord.goal_yaw
        )
        
        # (DIUBAH) Status 'queued' hanya diset di NavigationGoal
        db_goal = models.NavigationGoal(
            order=db_order, # Tautkan ke order yang baru dibuat
            status=schemas.OrderStatus.QUEUED.value,
            goal_x=db_order.goal_x,
            goal_y=db_order.goal_y,
            goal_yaw=db_order.goal_yaw
        )
        
        db.add(db_order)
        # Tidak perlu db.add(db_goal) secara eksplisit jika cascade sudah diatur
        created_orders.append(db_order)

    db.commit()
    for order in created_orders:
        db.refresh(order)
        # Pastikan relasinya juga di-refresh jika perlu
        if order.navigation_goal:
            db.refresh(order.navigation_goal)
            
    return created_orders

def update_order_status(db: Session, order_id: int, new_status: schemas.OrderStatus) -> models.Order:
    # (LOGIKA DIUBAH TOTAL)
    # Fungsi ini sekarang mencari order, lalu mengubah status NavigationGoal yang tertaut.
    db_order = (
        db.query(models.Order)
        .options(joinedload(models.Order.navigation_goal))
        .filter(models.Order.id == order_id)
        .first()
    )
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if not db_order.navigation_goal:
        raise HTTPException(status_code=404, detail="Associated Navigation Goal for this order not found")
    
    # Update status di NavigationGoal, bukan di Order
    db_order.navigation_goal.status = new_status.value
        
    db.commit()
    db.refresh(db_order)
    db.refresh(db_order.navigation_goal)
    return db_order

# === Fungsi untuk Navigation Goals ===

def get_navigation_goal(db: Session, goal_id: int):
    return db.query(models.NavigationGoal).filter(models.NavigationGoal.id == goal_id).first()

def get_navigation_goals_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    return db.query(models.NavigationGoal).filter(models.NavigationGoal.status == status).order_by(models.NavigationGoal.created_at.asc()).offset(skip).limit(limit).all()

def update_navigation_goal_status(db: Session, goal_id: int, new_status: schemas.GoalStatus) -> models.NavigationGoal:
    """Memperbarui status navigation goal. Ini adalah satu-satunya sumber kebenaran."""
    db_goal = get_navigation_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Navigation Goal not found")

    db_goal.status = new_status.value
    
    # (DIUBAH) Baris untuk mengupdate order.status dihapus karena sudah tidak ada.
    # if db_goal.order:
    #     db_goal.order.status = new_status.value
        
    db.commit()
    db.refresh(db_goal)
    return db_goal

def update_navigation_goal_meta(db: Session, goal_id: int, meta_data: schemas.NavigationGoalUpdateMeta) -> models.NavigationGoal:
    db_goal = get_navigation_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Navigation Goal not found")
    
    db_goal.meta = meta_data.meta
    db.commit()
    db.refresh(db_goal)
    return db_goal