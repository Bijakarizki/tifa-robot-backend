from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from typing import List

# === Fungsi untuk Tabel (Tables) ===

def get_table(db: Session, table_id: int):
    return db.query(models.Table).filter(models.Table.id == table_id).first()

def get_table_by_name(db: Session, table_name: str):
    return db.query(models.Table).filter(models.Table.table_number == table_name).first()

def get_tables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Table).offset(skip).limit(limit).all()

def create_table(db: Session, table: schemas.TableCreate):
    table_number_to_add = table.table_number
    predefined_table = db.query(models.PredefinedTable).filter(models.PredefinedTable.table_number == table_number_to_add).first()
    if not predefined_table:
        raise HTTPException(status_code=400, detail=f"Table '{table_number_to_add}' is not a valid predefined table.")
    existing_table = get_table_by_name(db, table_name=table_number_to_add)
    if existing_table:
        raise HTTPException(status_code=400, detail=f"Table '{table_number_to_add}' has already been added.")
    db_table = models.Table(table_number=predefined_table.table_number, coordinates=predefined_table.coordinates)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

def delete_table(db: Session, table_id: int):
    db_table = db.query(models.Table).filter(models.Table.id == table_id).first()
    if db_table:
        db.delete(db_table)
        db.commit()
        return db_table
    return None

# === Fungsi untuk Pesanan (Orders) ===

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(models.Order.id.desc()).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.model_dump(), status=0)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# (DIUBAH) Fungsi untuk membuat banyak pesanan sekaligus
def create_orders_bulk(db: Session, orders: List[schemas.OrderCreate]):
    created_orders = []
    for order_data in orders:
        # DIUBAH KEMBALI: Status diatur ke 0 (Siap Antar)
        # Ini adalah status yang akan dibaca oleh robot.
        db_order = models.Order(**order_data.model_dump(), status=0)
        db.add(db_order)
        created_orders.append(db_order)
    db.commit()
    for db_order in created_orders:
        db.refresh(db_order)
    return created_orders

# Fungsi untuk update status pesanan
def update_order_status(db: Session, order_id: int, new_status: int):
    db_order = get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return db_order