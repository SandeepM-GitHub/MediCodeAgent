from backend.data.db import init_db, SessionLocal, ICD10Code, CPTCode

# A small, highly relevant sample of medical codes for our testing
SAMPLE_ICD10 = [
    {"code": "J02.9", "description": "Acute pharyngitis, unspecified (Sore throat)"},
    {"code": "J03.90", "description": "Acute tonsillitis, unspecified"},
    {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
    {"code": "I10", "description": "Essential (primary) hypertension"},
    {"code": "R05.9", "description": "Cough, unspecified"}
]

SAMPLE_CPT = [
    {"code": "99213", "description": "Office or other outpatient visit for the evaluation and management of an established patient (Low-moderate complexity)"},
    {"code": "99214", "description": "Office or other outpatient visit, established patient (Moderate-high complexity)"},
    {"code": "87880", "description": "Infectious agent antigen detection by immunoassay with direct optical observation; Streptococcus, group A (Rapid strep test)"},
    {"code": "36415", "description": "Collection of venous blood by venipuncture (Blood draw)"},
    {"code": "93000", "description": "Electrocardiogram, routine ECG with at least 12 leads; with interpretation and report"}
]

def seed_database():
    """Populates the database with sample codes."""
    print("Initializing database tables...")
    init_db()

    db = SessionLocal()
    try: 
        # Check if we already have data to avoid duplicates
        if db.query(ICD10Code).first():
            print("Database already seeded! Skipping.")
            return
        
        print("Inserting ICD-10 codes...")
        for item in SAMPLE_ICD10:
            db.add(ICD10Code(code=item["code"], description=item["description"]))
            
        print("Inserting CPT codes...")
        for item in SAMPLE_CPT:
            db.add(CPTCode(code=item["code"], description=item["description"]))
            
        # Commit the transaction to save the data
        db.commit()
        print("Successfully seeded the database!")

    except Exception as e:
        db.rollback()
        print(f"An error occured: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()