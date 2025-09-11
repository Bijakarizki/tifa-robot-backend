# schemas.py

from pydantic import BaseModel
from typing import List
from datetime import datetime
from enum import Enum

# --- (BARU) Skema untuk Tabel Koordinat ---

class TableCoordinateBase(BaseModel):
    table_number: str
    goal_x: float
    goal_y: float
    goal_yaw: float

class TableCoordinateCreate(TableCoordinateBase):
    pass

class TableCoordinateResponse(TableCoordinateBase):
    id: int
    class Config:
        from_attributes = True

# --- (BARU) Enum untuk validasi status ---

class OrderStatus(str, Enum):
    QUEUED = "queued"
    READY = "ready"
    SUCCEEDED = "succeeded"
    
# --- (DIUBAH) Skema untuk Pesanan ---

class OrderBase(BaseModel):
    table_number: str

class OrderCreate(BaseModel):
    table_number: str

class OrderCreateBulk(BaseModel):
    orders: List[OrderCreate]

class OrderUpdateStatus(BaseModel):
    status: OrderStatus # Menggunakan Enum untuk validasi

class OrderResponse(OrderBase):
    id: int
    status: str
    goal_x: float
    goal_y: float
    goal_yaw: float
    class Config:
        from_attributes = True

# --- (DIUBAH) Skema untuk Navigation Goals ---

# Enum disesuaikan dengan yang baru (meskipun isinya sama dengan OrderStatus)
class GoalStatus(str, Enum):
    QUEUED = "queued"
    READY = "ready"
    SUCCEEDED = "succeeded"

class NavigationGoalUpdateStatus(BaseModel):
    status: GoalStatus

class NavigationGoalResponse(BaseModel):
    id: int
    order_id: int
    status: str
    goal_x: float
    goal_y: float
    goal_yaw: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True