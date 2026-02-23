import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the path where the SQLite database file will live
DB_PATH = os.path.join(os.path.dirname(__file__), "medical.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Initialize the SQAlchemy engine
# check_same_thread = False is needed for SQLite when used with web frameworks like FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()

class ICD10Code(Base):
    """Table to store diagnostic codes."""
    __tablename__ = "icd10_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)

class CPTCode(Base):
    """Table to store procedure codes."""
    __tablename__ = "cpt_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)

def init_db():
    """Creates the tables in the database if they dont exist."""
    Base.metadata.create_all(bind=engine)