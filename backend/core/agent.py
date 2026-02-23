import json
import operator
from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

# Import our local components
from backend.core.llm import get_llm
from backend.core.state import ClaimState
from backend.mcp.server import search_icd10, search_cpt # Reuse our smart search tools!

# ---------- Node 1: EXTRACTION -------------------
def extract_entities(state: ClaimState):
    """
    Uses Llama 3.2 to parse the raw text and find medical terms.
    """
    print("--- Node: Extraction ---")
    note = state["clinical_note"]

    # Strict prompt to force JSON output
    prompt = f""" 
    you are medical coding assistant. Extract the main DIAGNOSIS (condition) and PROCEDURE (treatement) from the text below.
    Return ONLY a JSON object with keys "diagnosis" and "procedure". Do not add any conversational text.
    
    TEXT: "{note}"
    """

    llm = get_llm()
    response = llm.invoke(prompt)

    # Basic cleanup to parse JSON from LLM response
    content = response.content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    try: 
        data = json.loads(content)
        return {
            "extracted_diagnosis": data.get("diagnosis", ""),
            "extracted_procedure": data.get("procedure", ""),
            "messages": ["Extracted entities successfully."]
        }
    except json.JSONDecodeError:
        return {
            "messages": ["Error: LLM failed to output valid JSON."]
        }
    
# ---------- Node 2: CODING (TOOL USE) ------------
def lookup_codes(state: ClaimState): 
    """
    Takes the extracted terms and searches our local FAISS Vector DB.
    """
    print("--- Node: Coding Lookup ---")

    diag_query = state.get("extracted_diagnosis", "")
    proc_query = state.get("extracted_procedure", "")

    icd_results = []
    cpt_results = []

    # Use out tools if we have queries
    if diag_query: 
        print(f"Searching ICD-10 for: {diag_query}")
        icd_results_str = search_icd10(diag_query) # Calls our local FAISS logic
        icd_results.append(icd_results_str)

    if proc_query: 
        print(f"Searching CPT for: {proc_query}")
        cpt_results_str = search_cpt(proc_query) # Calls our local FAISS logic
        cpt_results.append(cpt_results_str)

    return {
        "icd10_candidates": icd_results,
        "cpt_candidates": cpt_results,
        "messages": ["Performed vector search lookup."]
    }

# ---------- Node 3: VALIDATION and DECISION -------
def finalize_coding(state: ClaimState): 
    """
    Review the tool results and pick the best code.
    """
    print("--- Node: Final Decision ---")

    prompt = f"""
    You are a Senior Medical Coder. 
    
    1. Analyze the PATIENT NOTE: "{state['clinical_note']}"
    2. Review the ICD-10 SEARCH RESULTS: {state['icd10_candidates']}
    3. Review the CPT SEARCH RESULTS: {state['cpt_candidates']}
    
    Task: Select the EXACT code from the results that best matches the note. 
    If no code is a good match, state "None".
    
    Return ONLY a JSON object:
    {{
        "final_icd10": "Code",
        "final_cpt": "Code",
        "reasoning": "Brief explanation of why these codes were chosen based on the evidence.",
        "confidence": 0.99
    }}
    """
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    # Clean up JSON again
    content = response.content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    try:
        data = json.loads(content)
        return {
            "final_icd10_code": data.get("final_icd10"),
            "final_cpt_code": data.get("final_cpt"),
            "explanation": data.get("reasoning"),
            "confidence_score": data.get("confidence", 0.0),
            "status": "approved" if data.get("confidence", 0.0) > 0.8 else "review_needed"
        }
    except:
        return {"status": "error", "messages": ["Failed to parse decision."]}
    
# ---------- BUILD THE GRAPH -----------------------
def build_agent():
    workflow = StateGraph(ClaimState)

    # Add Nodes
    workflow.add_node("extract", extract_entities)
    workflow.add_node("lookup", lookup_codes)
    workflow.add_node("decide", finalize_coding)

    # Add Edges (The flow)
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "lookup")
    workflow.add_edge("lookup", "decide")
    workflow.add_edge("decide", END)

    return workflow.compile()