from fastapi import FastAPI
from pydantic import BaseModel
from backend.core.llm import get_llm

# Initialize the FastAPI application
app = FastAPI(
    title = "MediCodeAgent API",
    description= "Transparent and Robust API for  medical coding, billing, and revenue cycle automation backend system",
    version= "1.0.0"
)

# We use Pydantic to strictly define what incoming data should look like
class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    """
    Root endpoint to verify the server is alive
    """
    return {"message": "Welcome to MedicodeAgent API"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Later, we will expand this to check if Ollama and out Databases are running.
    """
    return {
        "status": "healthy",
        "service": "MedicodeAgent Core",
        "version": "1.0.0"
    }

# LLM Test Endpoint
@app.post("/api/test-llm")
async def test_llm(request: PromptRequest):
    """"
    Test endpoint to verify our FastAPI server can talk to local Ollama.
    """
    llm = get_llm()
    try:
        # Send the prompt to the local Llama 3.2 model
        response = llm.invoke(request.prompt)
        return {
            "response": response.content
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Make sure Ollama app is running in the background!"
        }