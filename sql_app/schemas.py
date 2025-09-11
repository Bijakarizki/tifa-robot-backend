# schemas.py

from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum

# --- TableCoordinateBase tidak berubah ---
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

# --- OrderStatus tidak berubah ---
class OrderStatus(str, Enum):
    QUEUED = "queued"
    READY = "ready"
    SUCCEEDED = "succeeded"

# --- Skema Pesanan ---
class OrderBase(BaseModel):
    table_number: str

class OrderCreate(BaseModel):
    table_number: str
    # 'meta' DIHAPUS dari sini, frontend tidak bisa mengirimnya lagi.

class OrderCreateBulk(BaseModel):
    orders: List[OrderCreate]

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderResponse(OrderBase):
    id: int
    status: str
    goal_x: float | None = None
    goal_y: float | None = None
    goal_yaw: float | None = None
    class Config:
        from_attributes = True

# --- Skema Navigation Goal ---
class GoalStatus(str, Enum):
    QUEUED = "queued"
    READY = "ready"
    SUCCEEDED = "succeeded"

class NavigationGoalUpdateStatus(BaseModel):
    status: GoalStatus

# (BARU) Skema khusus untuk robot mengupdate kolom meta
class NavigationGoalUpdateMeta(BaseModel):
    meta: Dict[str, Any]

# Pastikan 'meta' tetap ada di response agar bisa dilihat
class NavigationGoalResponse(BaseModel):
    id: int
    order_id: int
    status: str
    goal_x: float
    goal_y: float
    goal_yaw: float
    meta: Dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True