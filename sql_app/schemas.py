# schemas.py

from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum
from . import models

# --- TableCoordinate tidak berubah ---
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
    # (DIUBAH) Tambahkan created_at ke skema respons
    created_at: datetime 

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, order: models.Order) -> OrderResponse:
        return cls(
            id=order.id,
            table_number=order.table_number,
            status=order.navigation_goal.status if order.navigation_goal else "unknown",
            goal_x=order.goal_x,
            goal_y=order.goal_y,
            goal_yaw=order.goal_yaw,
            # (DIUBAH) Ambil nilai created_at dari model Order
            created_at=order.created_at 
        )

# --- Skema Navigation Goal tidak berubah ---
class GoalStatus(str, Enum):
    QUEUED = "queued"
    READY = "ready"
    SUCCEEDED = "succeeded"

class NavigationGoalUpdateStatus(BaseModel):
    status: GoalStatus

class NavigationGoalUpdateMeta(BaseModel):
    meta: Dict[str, Any]

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