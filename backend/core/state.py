from typing import TypedDict, List, Optional

class ClaimState(TypedDict):
    """
    Defines the 'memory' of our agent.
    This dictionary is passed between every node in the graph.
    """
    # Input
    clinical_note: str

    # Process Data
    extracted_diagnosis: Optional[str] # Raw text extracted from note
    extracted_procedure: Optional[str] # Raw text extracted from note

    # Tool Outputs (From FAISS)
    icd10_candidates: List[str]
    cpt_candidates: List[str]

    # Final Decisions
    final_icd10_code: Optional[str]
    final_cpt_code: Optional[str]
    explanation: Optional[str]
    confidence_score: float

    # Payer Decision Fields
    status: str # 'review_needed', 'approved', 'rejected'
    rejection_reason: Optional[str]
    rule_id: Optional[str]

    # Log of what happened
    messages: List[str] 