from sqlalchemy import Column, Integer, String
from .database import Base

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True)
    # Diubah dari Integer menjadi String
    coordinates = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(Integer, index=True)
    # tray_position dihapus
    table_number = Column(String)
    status = Column(Integer, default=0)