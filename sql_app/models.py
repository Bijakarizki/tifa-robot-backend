# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
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
    # KOLOM STATUS DIHAPUS DARI SINI
    # status = Column(String, index=True, default="queued") 
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)
    
    # Relasi ini sekarang menjadi kunci untuk mendapatkan status
    navigation_goal = relationship("NavigationGoal", back_populates="order", uselist=False, cascade="all, delete-orphan")

class NavigationGoal(Base):
    __tablename__ = "navigation_goals"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    # INI ADALAH SATU-SATUNYA SUMBER KEBENARAN STATUS
    status = Column(String, index=True, nullable=False)
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)
    frame_id = Column(String, default="map")
    meta = Column(JSONB, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    order = relationship("Order", back_populates="navigation_goal")