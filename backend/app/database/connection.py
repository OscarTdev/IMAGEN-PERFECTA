import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def _resolve_db_url() -> str:
    """DB original: MySQL `imagen_perfecta` (solo tablas).
    Variables: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME.
    """
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "imagen_perfecta")
    creds = f"{user}:{password}@" if password else f"{user}@"
    return f"mysql+pymysql://{creds}{host}:{port}/{db_name}"

SQLALCHEMY_DATABASE_URL = _resolve_db_url()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
