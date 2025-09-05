import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Muat environment variables dari file .env
load_dotenv()

# Ambil URL koneksi dari environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Pastikan variabel DATABASE_URL ada
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check your .env file.")

# Buat engine SQLAlchemy untuk koneksi
engine = create_engine(DATABASE_URL)

# Buat session factory, ini akan membuat sesi database baru setiap kali dipanggil
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model ORM (models.py akan mewarisi dari ini)
Base = declarative_base()

# Fungsi dependency yang akan di-inject oleh FastAPI ke setiap endpoint
# Ini memastikan setiap request mendapatkan sesi database yang terisolasi dan ditutup setelah selesai.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()