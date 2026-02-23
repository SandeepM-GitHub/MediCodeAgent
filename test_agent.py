from backend.core.agent import build_agent

def run_test():
    agent = build_agent()

    # A test case: Sore throat (should map to ICD J02.9) and Strep Test (CPT 87880)
    test_note = "Patient complains of severe sore throat. Performed rapid strep test."
    
    print(f"Input Note: {test_note}\n")
    print("Running Agent Pipeline...\n")
    
    initial_state = {"clinical_note": test_note, "messages": []}

    # Run the graph
    result = agent.invoke(initial_state)

    print("\n---------------- FINAL RESULT ----------------")
    print(f"Extracted Diagnosis: {result.get('extracted_diagnosis')}")
    print(f"Extracted Procedure: {result.get('extracted_procedure')}")
    print(f"Selected ICD-10:     {result.get('final_icd10_code')}")
    print(f"Selected CPT:        {result.get('final_cpt_code')}")
    print(f"Confidence:          {result.get('confidence_score')}")
    print(f"Explanation:         {result.get('explanation')}")
    print("----------------------------------------------")

if __name__ == "__main__":
    run_test()