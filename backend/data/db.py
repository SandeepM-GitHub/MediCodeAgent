import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
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

class Claim(Base):
    """Table to store the entire lifecycle of a medical claim."""
    __tablename__ = "claims"
    id = Column(Integer, primary_key= True, index= True)

    # Input Data
    clinical_note = Column(Text, nullable=False)
    timestamp = Column(DateTime, default= datetime.datetime.now(datetime.timezone.utc))

    # Extracted entities (Raw text from LLM)
    extracted_diagnosis =  Column(String, nullable= True)
    extracted_procedure =  Column(String, nullable= True)

    # Final coding (From Vector Search + Agent Decision)
    icd10_code = Column(String, nullable= True)
    cpt_code = Column(String, nullable= True)
    confidence_score = Column(Float, default= 0.0)
    explanation = Column(Text, nullable= True)

    # Payer Status (The "Money" part)
    status = Column(String, default= "pending")
    rejection_reason = Column(String, nullable= True)

    # Payment Details
    payment_amount = Column(Float, default= 0.0)
    stripe_transaction_id = Column(String, nullable= True)

def init_db():
    """Creates the tables in the database if they dont exist."""
    Base.metadata.create_all(bind=engine)