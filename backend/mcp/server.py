import os
import json
import faiss
import numpy as np
import torch
from fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from backend.data.db import SessionLocal, ICD10Code, CPTCode

# 1. Initialize the FastMCP server
# This acts just like the FastAPI 'app', but specifically for AI tools
mcp = FastMCP("MediCodeMCP")

# 2. Setup Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ICD10_INDEX_PATH = os.path.join(DATA_DIR, "icd10.index")
CPT_INDEX_PATH = os.path.join(DATA_DIR, "cpt.index")
META_PATH = os.path.join(DATA_DIR, "vector_meta.json")

# 3. Load Model and FAISS Indexes Globally (so they stay in memory)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Starting MCP Server. Loading embedding model on: {device.upper()}")
embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)

# Load FAISS indexes into memory
index_icd10 = faiss.read_index(ICD10_INDEX_PATH)
index_cpt = faiss.read_index(CPT_INDEX_PATH)

# Load Metadata to map math back to readable text
with open(META_PATH, "r") as f:
    metadata = json.load(f)

# ------- MCP TOOLS ------- 

@mcp.tool()
def search_icd10(query: str) -> str:
    """
    Search for an ICD-10 diagnosis code based on a clinical text query.
    Uses semantic similarity. Returns the top 3 matches with confidence score.
    """

    # 4. Convert the user's query into a math vector
    query_vector = embedder.encode([query], normalize_embeddings= True)

    # 5. Search the FAISS index (k=3 means top 3 results)
    scores, indices = index_icd10.search(np.array(query_vector), k=3)

    # 6. Format the output with the mathematical confidence scores
    results = "Top ICD-10 Semantic Matches: \n"
    for i in range(len(indices[0])):
        idx = indices[0][i]
        score = scores[0][i]
        # Only show valid indices (in case db has fewer than 3 items)
        if idx != -1:
            item = metadata["icd10"][idx]
            # Convert math score (e.g., 0.9234) to a percentage format
            results += f"{i+1}) {item['code']} {item['desc']} (Score: {score:.2f})\n"
    return results 

    # db = SessionLocal()
    # try: 
    #     # Basic SQL 'LIKE' search
    #     results = db.query(ICD10Code).filter(ICD10Code.description.ilike
    #         (f"%{query}%")).limit(3).all()
        
    #     if not results:
    #         return "No matching ICD-10 codes found."
        
    #     # We format the output as a clear string so the LLM easily understands it
    #     formatted_results = "Top ICD-10 Matches: \n"
    #     for r in results:
    #         formatted_results += f"- Code: {r.code} | Description: {r.description}\n"
    #         return formatted_results
    # finally:
    #     db.close()

@mcp.tool()
def search_cpt(query: str) -> str:
    """
    Search for a CPT procedure code based on a clinical phrase.
    Uses semantic similarity. Returns the top 3 matches with confidence scores.
    """
    query_vector = embedder.encode([query], normalize_embeddings=True)
    scores, indices = index_cpt.search(np.array(query_vector), k=3)
    
    results = "Top CPT Semantic Matches:\n"
    for i in range(len(indices[0])):
        idx = indices[0][i]
        score = scores[0][i]
        if idx != -1:
            item = metadata["cpt"][idx]
            results += f"{i+1}) {item['code']} {item['desc']} (Score: {score:.2f})\n"
            
    return results

    # db = SessionLocal()
    # try:
    #     results = db.query(CPTCode).filter(CPTCode.description.ilike(f"%{query}%")).limit(3).all()
        
    #     if not results:
    #         return "No matching CPT codes found."
        
    #     formatted_results = "Top CPT Matches:\n"
    #     for r in results:
    #         formatted_results += f"- Code: {r.code} | Description: {r.description}\n"
    #     return formatted_results
    # finally:
    #     db.close()

@mcp.tool()
def validate_code(code: str, code_type: str) -> str:
    """
    Validate if an exact code exists in the database.
    code_type must be exactly 'icd10' or 'cpt'.
    """
    db = SessionLocal()
    try:
        if code_type.lower() == 'icd10':
            result = db.query(ICD10Code).filter(ICD10Code.code == code).first()
        elif code_type.lower() == 'cpt':
            result = db.query(CPTCode).filter(CPTCode.code == code).first()
        else:
            return f"Error: Unknown code_type '{code_type}'. Use 'icd10' or 'cpt'."
        
        if result:
            return f"VALID: {result.code} - {result.description}"
        return f"INVALID: Code {code} not found in {code_type.upper()} database."
    finally:
        db.close()

if __name__ == "__main__":
    # This allows us to run the server locally to test it
    mcp.run()