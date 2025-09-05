from sqlalchemy import Column, Integer, String
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