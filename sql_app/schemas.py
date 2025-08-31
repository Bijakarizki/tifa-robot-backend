from pydantic import BaseModel

# --- Skema untuk Tabel ---
class TableBase(BaseModel):
    table_number: str
    # Diubah dari int menjadi str
    coordinates: str

class TableCreate(TableBase):
    pass

class TableResponse(TableBase):
    id: int
    class Config:
        orm_mode = True

# --- Skema untuk Pesanan ---
class OrderBase(BaseModel):
    order_number: int
    # tray_position dihapus
    table_number: str

class OrderCreate(OrderBase):
    pass

class OrderUpdateStatus(BaseModel):
    status: int

class OrderResponse(OrderBase):
    id: int
    status: int
    class Config:
        orm_mode = True