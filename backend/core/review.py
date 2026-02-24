from backend.data.db import SessionLocal, Claim

def submit_human_review(claim_id: int, decision: str, reviewer_name: str, notes: str):
    """
    Simulates Stage 10: Human-in-the-loop.
    Allows a human to manually override a suspicious claim.
    """
    db = SessionLocal()
    try:
        # 1. Find the claim in the filing cabinet
        claim = db.query(Claim).filter(Claim.id == claim_id).first()

        if not claim:
            return "Error: Claim not found"
        
        if claim.status != "suspicious":
            return f"Notice: Claim {claim_id} is currently '{claim.status}', not pending review."
        
        # 2. Apply the Human's decision
        claim.status = decision.lower() # Will be 'approved' or 'rejected'
        claim.rejection_reason = f"Human Override by {reviewer_name}: {notes}"

        # 3. Save the override permanently
        db.commit()
        return f"SUCCESS: Claim {claim_id} manually marked as {decision.upper()}" 
    finally:
        db.close()