# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
# Pastikan Anda mengimpor JSONB untuk tipe data JSON
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

class TableCoordinate(Base):
    __tablename__ = "table_coordinates"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True, nullable=False)
    goal_x = Column(Float, nullable=False)
    goal_y = Column(Float, nullable=False)
    goal_yaw = Column(Float, nullable=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, index=True)
    status = Column(String, index=True, default="queued")
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)
    navigation_goal = relationship("NavigationGoal", back_pop_ulates="order", uselist=False, cascade="all, delete-orphan")

class NavigationGoal(Base):
    __tablename__ = "navigation_goals"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    
    # Status: "queued", "ready", "succeeded"
    status = Column(String, index=True)
    
    # Kolom Goal
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)
    
    frame_id = Column(String, default="map")
    
    # (INI BAGIAN PENTING) Kolom baru untuk data JSON dari robot
    # nullable=True berarti kolom ini boleh kosong saat pertama kali dibuat
    meta = Column(JSONB, nullable=True) 
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    order = relationship("Order", back_populates="navigation_goal")