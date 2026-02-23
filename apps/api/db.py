import os
from sqlalchemy import create_engine, text
from models import Base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://rag:rag@localhost:5432/ragdb",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def ping_db() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    return True

def check_pgvector() -> bool:
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    return True

def create_tables() -> None:
    """Create SQL tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()