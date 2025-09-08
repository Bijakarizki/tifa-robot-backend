from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True)
    coordinates = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(Integer, index=True)
    table_number = Column(String)
    status = Column(Integer, default=0)

# Model untuk membaca dari tabel master 'predefined_tables'
class PredefinedTable(Base):
    __tablename__ = "predefined_tables"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True)
    coordinates = Column(String)

# (KELAS BARU YANG DITAMBAHKAN)
class NavigationGoal(Base):
    __tablename__ = "navigation_goals"

    id = Column(Integer, primary_key=True, index=True)
    
    # Status: "queued", "running", "done"
    status = Column(String, index=True, default="queued")
    
    # Kolom Goal (menggunakan Float untuk desimal)
    goal_x = Column(Float)
    goal_y = Column(Float)
    goal_yaw = Column(Float)
    
    frame_id = Column(String, default="map")
    
    # Meta (menggunakan JSONB bawaan Postgres)
    meta = Column(JSONB, nullable=True)
    
    # Timestamp (otomatis diatur oleh database)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())