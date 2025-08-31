from .database import execute_query
from . import schemas

def get_table(table_id: int):
    sql = "SELECT id, table_number, coordinates FROM tables WHERE id = ?;"
    results = execute_query(sql, params=[table_id])
    return results[0] if results else None

def get_table_by_name(table_name: str):
    sql = "SELECT id, table_number, coordinates FROM tables WHERE table_number = ?;"
    results = execute_query(sql, params=[table_name])
    return results[0] if results else None

def get_tables(skip: int = 0, limit: int = 100):
    sql = "SELECT id, table_number, coordinates FROM tables LIMIT ? OFFSET ?;"
    return execute_query(sql, params=[limit, skip])

def create_table(table: schemas.TableCreate):
    # Insert data ke database
    sql_insert = "INSERT INTO tables (table_number, coordinates) VALUES (?, ?);"
    params = [table.table_number, table.coordinates]
    
    print(f"Creating table with data: table_number={table.table_number}, coordinates={table.coordinates}")
    
    execute_query(sql_insert, params=params)
    
    # Baca kembali data yang baru dimasukkan
    print(f"Reading back created table: {table.table_number}")
    new_table = get_table_by_name(table.table_number)
    
    print(f"Created table result: {new_table}")
    return new_table

def delete_table(table_id: int):
    table_to_delete = get_table(table_id)
    if not table_to_delete:
        return None
    sql = "DELETE FROM tables WHERE id = ?;"
    execute_query(sql, params=[table_id])
    return table_to_delete

# Orders functions
def get_order(order_id: int):
    sql = "SELECT id, order_number, table_number, status FROM orders WHERE id = ?;"
    results = execute_query(sql, params=[order_id])
    return results[0] if results else None

def get_order_by_number(order_number: int):
    sql = "SELECT id, order_number, table_number, status FROM orders WHERE order_number = ? ORDER BY id DESC LIMIT 1;"
    results = execute_query(sql, params=[order_number])
    return results[0] if results else None

def get_orders(skip: int = 0, limit: int = 100):
    sql = "SELECT id, order_number, table_number, status FROM orders LIMIT ? OFFSET ?;"
    return execute_query(sql, params=[limit, skip])

def create_orders_bulk(orders: list[schemas.OrderCreate]):
    created_orders = []
    for order in orders:
        sql_insert = "INSERT INTO orders (order_number, table_number, status) VALUES (?, ?, 0);"
        params = [order.order_number, order.table_number]
        execute_query(sql_insert, params=params)
        new_order = get_order_by_number(order.order_number)
        if new_order:
            created_orders.append(new_order)
    return created_orders

def update_order_status(order_id: int, status: int):
    sql_update = "UPDATE orders SET status = ? WHERE id = ?;"
    params = [status, order_id]
    execute_query(sql_update, params=params)
    return get_order(order_id)

def delete_order(order_id: int):
    order_to_delete = get_order(order_id)
    if not order_to_delete:
        return None
    sql = "DELETE FROM orders WHERE id = ?;"
    execute_query(sql, params=[order_id])
    return order_to_delete