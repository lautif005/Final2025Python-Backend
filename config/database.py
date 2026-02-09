import os
import logging
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Importamos los modelos para asegurar que SQLAlchemy los registre
from models.address import AddressModel  # noqa
from models.base_model import base
from models.bill import BillModel  # noqa
from models.category import CategoryModel  # noqa
from models.client import ClientModel  # noqa
from models.order import OrderModel  # noqa
from models.order_detail import OrderDetailModel  # noqa
from models.product import ProductModel  # noqa
from models.review import ReviewModel  # noqa

# Get logger
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(env_path)

# --- INICIO DEL CAMBIO MAESTRO ---

# 1. Intentamos obtener la URL directa (Render la entrega así)
database_url = os.getenv('DATABASE_URL')

if database_url:
    # 2. Si existe, aplicamos el PARCHE para Render (postgres -> postgresql)
    if database_url.startswith("postgres://"):
        DATABASE_URI = database_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URI = database_url
    logger.info("✅ Usando DATABASE_URL detectada (Render Mode)")
else:
    # 3. Si no existe, la construimos manualmente (Local Mode)
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    logger.info("💻 Usando configuración manual (Local Mode)")

# --- FIN DEL CAMBIO MAESTRO ---

# High-performance connection pool configuration
POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '50'))
MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '100'))
POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '10'))
POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))

# Create engine
engine = create_engine(
    DATABASE_URI,
    pool_pre_ping=True,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    echo=False,
    future=True,
)

# SessionLocal class for creating new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    try:
        # Importante: create_all usa el 'engine' que ya configuramos arriba
        base.metadata.create_all(engine)
        logger.info("✅ Tables created successfully.")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        # No lanzamos la excepción para que el servidor no se caiga si ya existen
        pass


def drop_database():
    """Drop all tables in the database."""
    try:
        base.metadata.drop_all(engine)
        logger.info("Tables dropped successfully.")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise


def check_connection() -> bool:
    """Check if database connection is working."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection established.")
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False