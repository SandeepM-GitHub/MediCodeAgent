def run_payer_rules(icd_code: str, cpt_code: str, confidence: float) -> dict:
    """
    Simulates an insurance company's adjudication rule engine.
    Evaluates the codes and returns the payer's decision.
    """

    # Rule 0: Missing data
    if not icd_code or not cpt_code:
        return {
            "status": "rejected",
            "reason": "Missing diagnosis or procedure code.",
            "rule_id": "R0_MISSING_DATA"
        }

    # Rule 1: AI Confidence threshold
    if confidence < 0.85:
        return {
            "status": "rejected",
            "reason": f"AI confidence ({confidence}) is below the 85% threshold.",
            "rule_id": "R1_LOW_CONFIDENCE"
        }
    
    # Rule 2: Medical Necessity (Cross-Walking)
    # If the procedure is a Rapid Strep Test (87880)...
    if "87880" in cpt_code:
        # ...the diagnosis MUST be related to a sore throat (J02 or J03 family)
        if "J02" not in icd_code and "J03" not in icd_code:
            return {
                "status": "rejected", 
                "reason": "Procedure 87880 (Strep Test) is not medically necessary for this diagnosis.", 
                "rule_id": "R2_MEDICAL_NECESSITY"
            }
    
    # If it passes all rules, the insurance company approves it!
    return {
        "status": "approved",
        "reason": "Claim meets all medical necessity rules.",
        "rule_id": "PASS"
    }