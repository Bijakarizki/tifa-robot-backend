from pydantic import BaseModel
from typing import List

# --- Skema untuk Tabel ---

class TableBase(BaseModel):
    table_number: str
    coordinates: str

class TableCreate(BaseModel):
    table_number: str

class TableResponse(TableBase):
    id: int
    class Config:
        from_attributes = True

# --- Skema untuk Pesanan ---

class OrderBase(BaseModel):
    order_number: int
    table_number: str

class OrderCreate(OrderBase):
    pass

# (BARU) Skema untuk menerima daftar pesanan
class OrderCreateBulk(BaseModel):
    orders: List[OrderCreate]

# (BARU) Skema untuk update status
class OrderUpdateStatus(BaseModel):
    status: int

class OrderResponse(OrderBase):
    id: int
    status: int
    class Config:
        from_attributes = True