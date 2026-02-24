from backend.core.agent import build_agent
from backend.core.review import submit_human_review
from backend.data.db import SessionLocal, Claim

def run_tests():
    agent = build_agent()

    print("\n" + "="*50)
    print("TEST 1: THE FRAUDULENT CLAIM (Rule 2: Mismatch)")
    print("="*50)
    # We try to bill a Strep Test (87880) for a twisted ankle.
    bad_note = "Patient came in with a twisted ankle. Performed rapid strep test."
    res1 = agent.invoke({"clinical_note": bad_note, "messages": []})
    # Debug
    print(f"\n[AI BRAIN] Selected ICD: {res1.get('final_icd10_code')}")
    print(f"[AI BRAIN] Selected CPT: {res1.get('final_cpt_code')}")
    
    print("\n" + "="*50)
    print("TEST 2: THE VAGUE CLAIM (Rule 1: Low Confidence)")
    print("="*50)
    # This vagueness will cause FAISS to return a low math score.
    vague_note = "Patient feels slightly unwell today."
    res2 = agent.invoke({"clinical_note": vague_note, "messages": []})
    # Debug
    print(f"\n[AI BRAIN] Selected ICD: {res2.get('final_icd10_code')}")
    print(f"[AI BRAIN] Selected CPT: {res2.get('final_cpt_code')}")
    
    print("\n" + "="*50)
    print("TEST 3: STAGE 10 HUMAN-IN-THE-LOOP OVERRIDE")
    print("="*50)

    # Artificially inject a 'suspicious' claim directly into the DB 
    # so we can reliably test the human override function.
    try: 
        db = SessionLocal()
        mock_claim = Claim(
        clinical_note="Mock claim: AI was unsure about a complex symptom.",
        icd10_code="J02.9",
        cpt_code="87880",
        confidence_score=0.60, # Intentionally low
        status="suspicious",
        rejection_reason="AI confidence (0.60) is below the 0.80 threshold."
        )
        db.add(mock_claim)
        db.commit()
        db.refresh(mock_claim)
        claim_id = mock_claim.id
    except Exception as e:
        print(f"Database error during mock claim creation: {e}")
        return
    finally:
        # CRITICAL: We must close this session so SQLite doesn't lock!
        db.close()

    print(f"Created a mock 'suspicious' claim in Database with ID: {claim_id}" )
    print("Human Auditor stepping in to review...")

    # We extract the Database ID of that vague claim we just saved
    try:
        result = submit_human_review(
            claim_id=claim_id, 
            decision="approved", 
            reviewer_name="Senior Medical Coder", 
            notes="Reviewed patient history manually. Proceed to billing."
        )
        print(f"\n{result}\n")
    except Exception as e:
        print(f"\n Error during human review: {e}\n")

if __name__ == "__main__":
    run_tests()