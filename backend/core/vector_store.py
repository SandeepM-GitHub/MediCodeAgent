import os
import json
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from backend.data.db import SessionLocal, ICD10Code, CPTCode

# Define where we will save our vector indexes and metadata
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ICD10_INDEX_PATH = os.path.join(DATA_DIR, "icd10.index")
CPT_INDEX_PATH = os.path.join(DATA_DIR, "cpt.index")
META_PATH = os.path.join(DATA_DIR, "vector_meta.json")

# Load a lightweight, free, local embedding model
# Detect Hardware (GPU vs CPU) and creates 384-dimensional vectors
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading embedding model on: {device.upper()}")

# 3. Load Model onto the selected hardware
embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)

def build_vector_db():
    """
    Reads the SQLite database, converts medical descriptions to vectors, 
    and saves them using FAISS for lightning-fast semantic search.
    """
    db = SessionLocal()
    try: 
        icd10_records = db.query(ICD10Code).all()
        cpt_records = db.query(CPTCode).all()

        if not icd10_records or not cpt_records:
            print("database is empty! Run seed.py first.")
            return
        
        print("Generating embeddings for ICD-10...")
        icd10_texts = [f"{r.code}: {r.description}" for r in icd10_records]
        # Generate vectors
        icd10_embeddings = embedder.encode(icd10_texts, normalize_embeddings=True)

        print("Generating embeddings for CPT...")
        cpt_texts = [f"{r.code}: {r.description}" for r in cpt_records]
        # Generate vectors
        cpt_embeddings = embedder.encode(cpt_texts, normalize_embeddings=True)

        # Create FAISS indexes using Inner Product (Cosine Similarity because we normalized)
        d = icd10_embeddings.shape[1] # Dimension size (384)

        index_icd10 = faiss.IndexFlatIP(d)
        index_icd10.add(np.array(icd10_embeddings))
        faiss.write_index(index_icd10, ICD10_INDEX_PATH)

        index_cpt = faiss.IndexFlatIP(d)
        index_cpt.add(np.array(cpt_embeddings))
        faiss.write_index(index_cpt, CPT_INDEX_PATH)

        # Save metadata mapping so we know which vector belongs to which code
        metadata = {
            "icd10": [{"code": r.code, "desc": r.description} for r in icd10_records],
            "cpt": [{"code": r.code, "desc": r.description} for r in cpt_records]
        }
        with open(META_PATH, "w") as f:
            json.dump(metadata, f)

        print("FAISS Vector DB successfully built and saved locally!")

    finally:
        db.close()

if __name__ == "__main__":
    build_vector_db()


