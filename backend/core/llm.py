from langchain_ollama import ChatOllama

def get_llm():
    """
    Initializes and return the local Llama 3.2 model via Ollama.
    We set temperature to 0.0 because medical coding requires strict factual accuracy,
    not creative hallucinations.
    """
    llm = ChatOllama(
        model = "llama3.2",
        temperature = 0.0,
    )
    return llm