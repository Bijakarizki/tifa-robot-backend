from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas

# === Fungsi untuk Tabel (Tables) ===

def get_table(db: Session, table_id: int):
    return db.query(models.Table).filter(models.Table.id == table_id).first()

def get_table_by_name(db: Session, table_name: str):
    return db.query(models.Table).filter(models.Table.table_number == table_name).first()

def get_tables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Table).offset(skip).limit(limit).all()

def create_table(db: Session, table: schemas.TableCreate):
    """
    Membuat meja baru dengan memvalidasi terlebih dahulu ke tabel master 'predefined_tables'.
    """
    table_number_to_add = table.table_number

    # Langkah 1: Query ke tabel master untuk mencari meja yang diminta.
    predefined_table = db.query(models.PredefinedTable).filter(
        models.PredefinedTable.table_number == table_number_to_add
    ).first()

    # Langkah 2: Jika tidak ditemukan di tabel master, tolak permintaan.
    if not predefined_table:
        raise HTTPException(
            status_code=400,
            detail=f"Table '{table_number_to_add}' is not a valid predefined table."
        )

    # Langkah 3: Cek apakah meja ini sudah pernah ditambahkan sebelumnya di tabel 'tables'.
    existing_table = get_table_by_name(db, table_name=table_number_to_add)
    if existing_table:
        raise HTTPException(
            status_code=400,
            detail=f"Table '{table_number_to_add}' has already been added."
        )

    # Langkah 4: Jika valid dan belum ada, buat entri baru di tabel 'tables'.
    db_table = models.Table(
        table_number=predefined_table.table_number,
        coordinates=predefined_table.coordinates  # Ambil koordinat dari tabel master
    )
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
    return db.query(models.Order).offset(skip).limit(limit).all()