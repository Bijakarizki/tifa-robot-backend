from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas

# === Functions for Tables ===

def get_table(db: Session, table_id: int):
    return db.query(models.Table).filter(models.Table.id == table_id).first()

def get_table_by_name(db: Session, table_name: str):
    return db.query(models.Table).filter(models.Table.table_number == table_name).first()

def get_tables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Table).offset(skip).limit(limit).all()

def create_table(db: Session, table: schemas.TableCreate):
    """
    Creates a new table by first validating against the 'predefined_tables' master table.
    """
    table_number_to_add = table.table_number

    # Step 1: Query the master table for the requested table.
    predefined_table = db.query(models.PredefinedTable).filter(
        models.PredefinedTable.table_number == table_number_to_add
    ).first()

    # Step 2: If not found in the master table, reject the request.
    if not predefined_table:
        raise HTTPException(
            status_code=400,
            detail=f"Table '{table_number_to_add}' is not a valid predefined table."
        )

    # Step 3: Check if this table has already been added to the 'tables' table.
    existing_table = get_table_by_name(db, table_name=table_number_to_add)
    if existing_table:
        raise HTTPException(
            status_code=400,
            detail=f"Table '{table_number_to_add}' has already been added."
        )

    # Step 4: If valid and not yet present, create the new entry in the 'tables' table.
    db_table = models.Table(
        table_number=predefined_table.table_number,
        coordinates=predefined_table.coordinates  # Get coordinates from the master table
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

# === Functions for Orders ===

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

# (NEW) Function to create a new order
def create_order(db: Session, order: schemas.OrderCreate):
    """Creates a new order entry in the database."""
    db_order = models.Order(
        order_number=order.order_number,
        table_number=order.table_number,
        status=0  # Default status: 0 for 'New'
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

