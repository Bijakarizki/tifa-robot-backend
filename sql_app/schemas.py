from pydantic import BaseModel

# --- Skema untuk Tabel ---

class TableBase(BaseModel):
    table_number: str
    coordinates: str

# DIUBAH: Skema ini sekarang hanya berisi table_number.
# FastAPI akan menggunakan ini untuk memvalidasi request body dari frontend.
class TableCreate(BaseModel):
    table_number: str

class TableResponse(TableBase):
    id: int

    class Config:
        # Pydantic v2 menggunakan `from_attributes` bukan `orm_mode`
        # Namun, kita biarkan `orm_mode` untuk kompatibilitas jika Pydantic Anda v1
        orm_mode = True
        from_attributes = True


# --- Skema untuk Pesanan (tetap sama) ---

class OrderBase(BaseModel):
    order_number: int
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
        from_attributes = True