from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import crud, schemas

app = FastAPI(
    title="TIFA Robot Control API",
    description="API untuk mengelola pesanan dan meja untuk robot TIFA (Direct API version).",
    version="2.0.0",
)

origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TIFA Robot Control API"}

# === ENDPOINT TEST UNTUK DEBUGGING ===
@app.get("/test/db", tags=["Debug"])
def test_database():
    """Test koneksi database dengan query sederhana"""
    try:
        from .database import execute_query
        result = execute_query("SELECT 1 as test;")
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test/tables-raw", tags=["Debug"])
def test_tables_raw():
    """Test query tabel secara langsung"""
    try:
        from .database import execute_query
        result = execute_query("SELECT * FROM tables;")
        return {"success": True, "result": result, "count": len(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/test/insert", tags=["Debug"])
def test_insert():
    """Test insert data langsung ke database"""
    try:
        from .database import execute_query
        
        # Test insert
        print("=== TESTING DIRECT INSERT ===")
        insert_result = execute_query(
            "INSERT INTO tables (table_number, coordinates) VALUES (?, ?);",
            params=["DEBUG_TABLE", "100,200"]
        )
        print(f"Insert result: {insert_result}")
        
        # Test select setelah insert
        select_result = execute_query("SELECT * FROM tables WHERE table_number = ?;", params=["DEBUG_TABLE"])
        print(f"Select result: {select_result}")
        
        return {
            "success": True, 
            "insert_result": insert_result,
            "select_result": select_result,
            "message": "Direct insert test completed"
        }
    except Exception as e:
        print(f"Insert test error: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/test/cleanup", tags=["Debug"])
def test_cleanup():
    """Hapus data test"""
    try:
        from .database import execute_query
        result = execute_query("DELETE FROM tables WHERE table_number = ?;", params=["DEBUG_TABLE"])
        return {"success": True, "result": result, "message": "Test data cleaned up"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# === API MEJA ===
@app.post("/tables/", response_model=schemas.TableResponse, tags=["Tables"])
def create_table(table: schemas.TableCreate):
    print(f"=== POST /tables/ STARTED ===")
    print(f"Input data: {table.dict()}")
    
    # Cek duplikat
    print("Checking for existing table...")
    existing_table = crud.get_table_by_name(table_name=table.table_number)
    print(f"Existing table check result: {existing_table}")
    
    if existing_table:
        raise HTTPException(status_code=400, detail="Table with this number already exists")
    
    # Buat table
    print("Creating new table...")
    try:
        new_table = crud.create_table(table=table)
        print(f"Create table result: {new_table}")
        
        # Pastikan data berhasil dibuat
        if not new_table:
            print("ERROR: create_table returned None or empty")
            raise HTTPException(status_code=500, detail="Failed to create table - no data returned")
        
        print(f"=== POST /tables/ SUCCESS ===")
        return new_table
        
    except Exception as e:
        print(f"ERROR in create_table: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")

@app.get("/tables/", response_model=List[schemas.TableResponse], tags=["Tables"])
def read_tables(skip: int = 0, limit: int = 100):
    print(f"=== GET /tables/ STARTED ===")
    print(f"Parameters: skip={skip}, limit={limit}")
    
    try:
        tables = crud.get_tables(skip=skip, limit=limit)
        print(f"Found {len(tables)} tables")
        print(f"Tables data: {tables}")
        print(f"=== GET /tables/ SUCCESS ===")
        return tables
    except Exception as e:
        print(f"ERROR in get_tables: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

@app.get("/tables/{table_id}", response_model=schemas.TableResponse, tags=["Tables"])
def read_table(table_id: int):
    db_table = crud.get_table(table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@app.delete("/tables/{table_id}", tags=["Tables"])
def delete_table(table_id: int):
    db_table = crud.delete_table(table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"ok": True, "message": "Table deleted successfully"}

# === API PESANAN ===
@app.post("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def create_orders(orders: List[schemas.OrderCreate]):
    return crud.create_orders_bulk(orders=orders)

@app.get("/orders/", response_model=List[schemas.OrderResponse], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100):
    return crud.get_orders(skip=skip, limit=limit)

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse, tags=["Orders"])
def read_order(order_id: int):
    db_order = crud.get_order(order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}/status", response_model=schemas.OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_update: schemas.OrderUpdateStatus):
    db_order = crud.update_order_status(order_id=order_id, status=status_update.status)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.delete("/orders/{order_id}", tags=["Orders"])
def delete_order(order_id: int):
    db_order = crud.delete_order(order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"ok": True, "message": "Order deleted successfully"}