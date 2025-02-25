from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from endpoints.chat import Agent
import uuid
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Assistant API",
    description="A FastAPI service for cryptocurrency market information powered by CoinMarketCap",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    history: Optional[str]
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str

try:
    agent = Agent()
    logger.info("Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Agent: {str(e)}")
    raise

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get the agent chain with history
        agent_with_history = agent.agent(request.message)
        
        # Invoke the chain with the message
        response = agent_with_history.invoke(
            {"user_input": request.message},
            {"configurable": {"session_id": session_id}}
        )
        
        return ChatResponse(
            session_id=session_id,
            response=response['output']
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
