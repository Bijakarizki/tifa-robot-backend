from sqlalchemy.orm import Session
from . import models, schemas

# === Fungsi untuk Tabel (Tables) ===

def get_table(db: Session, table_id: int):
    return db.query(models.Table).filter(models.Table.id == table_id).first()

def get_table_by_name(db: Session, table_name: str):
    return db.query(models.Table).filter(models.Table.table_number == table_name).first()

def get_tables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Table).offset(skip).limit(limit).all()

# FUNGSI INI DIUBAH
def create_table(db: Session, table: schemas.TableCreate):
    # --- LOGIKA BARU UNTUK MENENTUKAN KOORDINAT ---
    # Di sini Anda bisa menambahkan logika yang lebih kompleks.
    # Misalnya, mencari nomor meja di dalam sebuah dictionary
    # untuk mendapatkan koordinat yang sudah ditentukan sebelumnya.
    # Untuk saat ini, kita gunakan nilai default.
    default_coordinates = "0,0"
    # -----------------------------------------------

    db_table = models.Table(
        table_number=table.table_number,
        coordinates=default_coordinates  # Menggunakan nilai yang ditentukan di backend
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

# === Fungsi untuk Pesanan (Orders) (tetap sama) ===

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()