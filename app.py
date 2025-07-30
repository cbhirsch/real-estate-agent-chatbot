from fastapi import FastAPI, HTTPException, Header, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import uuid
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# Import your chatbot components
from real_estate_agent import graph, State

# Load environment variables
load_dotenv()

app = FastAPI(title="Real Estate Agent API", version="1.0.0")

# Security setup
security = HTTPBearer()
API_KEYS = os.getenv("API_KEYS", "").split(",")  # Comma-separated list of valid API keys

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key from Authorization header"""
    api_key = credentials.credentials
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

class VAPIRequest(BaseModel):
    session_id: str
    user_message: str
    context: Optional[Dict[str, Any]] = None

class VAPIResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

# In-memory session storage (in production, use Redis or database)
sessions = {}

def verify_vapi_signature(authorization: str) -> bool:
    """Verify VAPI signature - implement your verification logic here"""
    # For now, just check if authorization header exists
    # In production, implement proper signature verification
    return authorization is not None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    """Main chat endpoint for the real estate agent"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create human message
        human_message = HumanMessage(content=request.message)
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {"messages": []}
        
        # Add human message to session
        sessions[session_id]["messages"].append(human_message)
        
        # Create state for the graph
        state = State(messages=sessions[session_id]["messages"])
        
        # Run the graph with thread_id for checkpointer
        config = {"configurable": {"thread_id": session_id}}
        result = graph.invoke(state, config=config)
        
        # Extract AI response
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        
        # Update session with AI response
        sessions[session_id]["messages"].append(ai_message)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/vapi/webhook", response_model=VAPIResponse)
async def vapi_webhook(
    request: VAPIRequest,
    authorization: str = Header(None)
):
    """VAPI webhook endpoint for voice integration"""
    try:
        # Verify the request is from VAPI
        if not verify_vapi_signature(authorization):
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Create human message
        human_message = HumanMessage(content=request.user_message)
        
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = {"messages": []}
        
        # Add human message to session
        sessions[request.session_id]["messages"].append(human_message)
        
        # Create state for the graph
        state = State(messages=sessions[request.session_id]["messages"])
        
        # Run the graph with thread_id for checkpointer
        config = {"configurable": {"thread_id": request.session_id}}
        result = graph.invoke(state, config=config)
        
        # Extract AI response
        ai_message = result["messages"][-1]
        response_text = ai_message.content
        
        # Update session with AI response
        sessions[request.session_id]["messages"].append(ai_message)
        
        return VAPIResponse(
            response=response_text,
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VAPI webhook error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Real Estate Agent API is running"}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """Get session history"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "type": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content
            }
            for msg in sessions[session_id]["messages"]
        ]
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str, api_key: str = Depends(verify_api_key)):
    """Delete a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": "Session deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)