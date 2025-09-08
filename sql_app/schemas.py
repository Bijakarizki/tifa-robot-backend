from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum

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


# --- (SKEMA BARU UNTUK NAVIGATION GOALS) ---

# Enum untuk validasi status
class GoalStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"

# Skema dasar untuk data input (tanpa ID atau timestamp)
class NavigationGoalBase(BaseModel):
    goal_x: float
    goal_y: float
    goal_yaw: float
    frame_id: str = "map"
    meta: Dict[str, Any] | None = None

# Skema untuk membuat data baru (mewarisi dari Base)
class NavigationGoalCreate(NavigationGoalBase):
    pass

# Skema untuk update status (mirip OrderUpdateStatus)
class NavigationGoalUpdateStatus(BaseModel):
    status: GoalStatus # Menggunakan Enum untuk validasi

# Skema Response (apa yang dikembalikan API)
class NavigationGoalResponse(NavigationGoalBase):
    id: int
    status: str # Bisa juga pakai GoalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True