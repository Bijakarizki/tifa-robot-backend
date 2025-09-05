from sqlalchemy.orm import Session
from . import models, schemas

# === Fungsi untuk Tabel (Tables) ===

def get_table(db: Session, table_id: int):
    """Mengambil satu meja berdasarkan ID-nya."""
    return db.query(models.Table).filter(models.Table.id == table_id).first()

def get_table_by_name(db: Session, table_name: str):
    """Mengambil satu meja berdasarkan nomor mejanya."""
    return db.query(models.Table).filter(models.Table.table_number == table_name).first()

def get_tables(db: Session, skip: int = 0, limit: int = 100):
    """Mengambil daftar semua meja dengan paginasi."""
    return db.query(models.Table).offset(skip).limit(limit).all()

def create_table(db: Session, table: schemas.TableCreate):
    """Membuat entri meja baru di database."""
    # Membuat objek model SQLAlchemy dari data Pydantic
    db_table = models.Table(
        table_number=table.table_number,
        coordinates=table.coordinates
    )
    # Menambahkan objek ke sesi
    db.add(db_table)
    # Menyimpan perubahan ke database
    db.commit()
    # Me-refresh objek untuk mendapatkan data yang baru dibuat (seperti ID)
    db.refresh(db_table)
    return db_table

def delete_table(db: Session, table_id: int):
    """Menghapus meja dari database berdasarkan ID."""
    db_table = get_table(db, table_id)
    if db_table:
        db.delete(db_table)
        db.commit()
        return db_table
    return None

# === Fungsi untuk Pesanan (Orders) ===

def get_order(db: Session, order_id: int):
    """Mengambil satu pesanan berdasarkan ID-nya."""
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    """Mengambil daftar semua pesanan dengan paginasi."""
    return db.query(models.Order).offset(skip).limit(limit).all()