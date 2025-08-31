from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import dengan try-catch untuk menghindari crash
try:
    from . import crud, schemas
except ImportError as e:
    print(f"Import error: {e}")
    crud = None
    schemas = None

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
    return {"message": "Welcome to TIFA Robot Control API", "status": "running"}

# === ENDPOINT TEST SEDERHANA ===
@app.get("/test/basic", tags=["Debug"])
def test_basic():
    """Test endpoint paling sederhana"""
    return {"success": True, "message": "Basic endpoint working"}

@app.get("/test/import", tags=["Debug"])
def test_import():
    """Test apakah import berhasil"""
    return {
        "crud_imported": crud is not None,
        "schemas_imported": schemas is not None
    }

@app.get("/test/db-simple", tags=["Debug"])
def test_database_simple():
    """Test koneksi database dengan error handling yang aman"""
    if not crud:
        return {"success": False, "error": "CRUD module not imported"}
    
    try:
        from .database import execute_query
        result = execute_query("SELECT 1 as test;")
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test/tables-count", tags=["Debug"])
def test_tables_count():
    """Test hitung tabel secara aman"""
    if not crud:
        return {"success": False, "error": "CRUD module not imported"}
    
    try:
        from .database import execute_query
        result = execute_query("SELECT COUNT(*) as count FROM tables;")
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/test/simple-insert", tags=["Debug"])
def test_simple_insert():
    """Test insert sederhana tanpa menggunakan CRUD"""
    try:
        from .database import execute_query
        import time
        
        # Generate table number yang unik
        test_table = f"TEST_{int(time.time())}"
        
        print(f"Testing insert with table_number: {test_table}")
        
        # Direct insert
        insert_result = execute_query(
            "INSERT INTO tables (table_number, coordinates) VALUES (?, ?);",
            params=[test_table, "999,888"]
        )
        print(f"Insert result: {insert_result}")
        
        # Check if inserted
        select_result = execute_query(
            "SELECT * FROM tables WHERE table_number = ?;",
            params=[test_table]
        )
        print(f"Select after insert: {select_result}")
        
        return {
            "success": True,
            "insert_result": insert_result,
            "select_result": select_result,
            "test_table": test_table
        }
        
    except Exception as e:
        print(f"Simple insert test error: {e}")
        return {"success": False, "error": str(e)}

# === API MEJA (VERSI AMAN) ===
@app.post("/tables/", tags=["Tables"])
def create_table(table: dict):  # Gunakan dict biasa dulu untuk menghindari Pydantic error
    """Create table dengan error handling yang lebih aman"""
    
    if not crud or not schemas:
        raise HTTPException(status_code=500, detail="Modules not loaded properly")
    
    try:
        print(f"=== POST /tables/ STARTED ===")
        print(f"Raw input: {table}")
        
        # Validasi manual input
        if 'table_number' not in table or 'coordinates' not in table:
            raise HTTPException(status_code=400, detail="Missing required fields: table_number, coordinates")
        
        table_number = str(table['table_number'])
        coordinates = str(table['coordinates'])
        
        print(f"Processed: table_number={table_number}, coordinates={coordinates}")
        
        # Cek duplikat
        existing_table = crud.get_table_by_name(table_name=table_number)
        if existing_table:
            raise HTTPException(status_code=400, detail="Table with this number already exists")
        
        # Direct insert tanpa menggunakan schemas dulu
        from .database import execute_query
        
        insert_result = execute_query(
            "INSERT INTO tables (table_number, coordinates) VALUES (?, ?);",
            params=[table_number, coordinates]
        )
        print(f"Insert result: {insert_result}")
        
        # Baca kembali data
        new_table = crud.get_table_by_name(table_number)
        print(f"Retrieved new table: {new_table}")
        
        if not new_table:
            raise HTTPException(status_code=500, detail="Table created but cannot retrieve")
        
        return new_table
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Unexpected error in create_table: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/tables/", tags=["Tables"])
def read_tables(skip: int = 0, limit: int = 100):
    """Get tables dengan error handling yang aman"""
    
    if not crud:
        raise HTTPException(status_code=500, detail="CRUD module not loaded")
    
    try:
        print(f"=== GET /tables/ STARTED ===")
        tables = crud.get_tables(skip=skip, limit=limit)
        print(f"Found {len(tables)} tables")
        return tables
    except Exception as e:
        print(f"Error in read_tables: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

@app.get("/tables/{table_id}", tags=["Tables"])
def read_table(table_id: int):
    if not crud:
        raise HTTPException(status_code=500, detail="CRUD module not loaded")
    
    db_table = crud.get_table(table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table

@app.delete("/tables/{table_id}", tags=["Tables"])
def delete_table(table_id: int):
    if not crud:
        raise HTTPException(status_code=500, detail="CRUD module not loaded")
    
    db_table = crud.delete_table(table_id=table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"ok": True, "message": "Table deleted successfully"}

# === API PESANAN ===
@app.get("/orders/", tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100):
    if not crud:
        raise HTTPException(status_code=500, detail="CRUD module not loaded")
    
    return crud.get_orders(skip=skip, limit=limit)