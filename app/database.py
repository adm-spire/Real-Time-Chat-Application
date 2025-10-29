from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DB_USER = "raunaq"
DB_PASSWORD = "raunaq"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mydb"

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Dependency function for FastAPI routes
def get_db():
    """
    Provides a database session for each request.
    Automatically closes the connection when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

