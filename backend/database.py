"""Motor de base de datos SQLAlchemy con migración automática de columnas."""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Añade columnas nuevas a tablas existentes sin borrar datos."""
    _pending = [
        ("projects", "chapters_mode",           "BOOLEAN DEFAULT 0"),
        ("projects", "chapter_duration_minutes", "INTEGER DEFAULT 20"),
        ("projects", "total_chapters",           "INTEGER DEFAULT 1"),
        ("projects", "error_message",            "TEXT"),
        ("scenes",   "chapter_number",           "INTEGER DEFAULT 1"),
    ]

    insp = inspect(engine)
    existing_tables = insp.get_table_names()

    with engine.connect() as conn:
        for table, col, definition in _pending:
            if table not in existing_tables:
                continue
            existing_cols = [c["name"] for c in insp.get_columns(table)]
            if col not in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {definition}"))
                except Exception:
                    pass  # ya existe o no es compatible
        conn.commit()
