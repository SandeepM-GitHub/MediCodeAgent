from backend.data.db import SessionLocal, Claim

db = SessionLocal()
claims = db.query(Claim).all()

print(f"\nFound {len(claims)} claims in the database:")
for c in claims:
    print(f"ID: {c.id} | Status: {c.status} | ICD-10: {c.icd10_code} | Confidence: {c.confidence_score}")

db.close()