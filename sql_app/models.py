# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# (BARU) Tabel master untuk menyimpan koordinat setiap meja.
# Ini adalah tabel 'koor' yang Anda minta.
class TableCoordinate(Base):
    __tablename__ = "table_coordinates"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True, nullable=False)
    goal_x = Column(Float, nullable=False)
    goal_y = Column(Float, nullable=False)
    goal_yaw = Column(Float, nullable=False)

# (DIUBAH) Tabel Order sekarang memiliki status string dan koordinatnya sendiri.
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, index=True)
    
    # Status diubah ke String, defaultnya 'queued' saat dibuat.
    # Alur: queued -> ready -> succeeded
    status = Column(String, index=True, default="queued")

    # Koordinat disalin ke sini dari TableCoordinate saat order dibuat.
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)

    # Relasi one-to-one ke NavigationGoal
    navigation_goal = relationship("NavigationGoal", back_populates="order", uselist=False, cascade="all, delete-orphan")

# (DIUBAH) Tabel NavigationGoal sekarang terhubung langsung ke Order.
class NavigationGoal(Base):
    __tablename__ = "navigation_goals"
    id = Column(Integer, primary_key=True, index=True)
    
    # (KUNCI) Foreign Key yang menghubungkan goal ini ke sebuah order.
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    
    # Status: "queued", "ready", "succeeded" (disinkronkan dari Order)
    status = Column(String, index=True)
    
    # Kolom Goal (disalin dari Order)
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)
    
    frame_id = Column(String, default="map")
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relasi kembali ke Order
    order = relationship("Order", back_populates="navigation_goal")