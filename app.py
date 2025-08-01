from fastapi import FastAPI, HTTPException, Header, Depends, Security, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import uuid
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import time
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from starlette.middleware.sessions import SessionMiddleware
import jwt

# Import your chatbot components
from real_estate_agent import graph, State

# Load environment variables
load_dotenv()

app = FastAPI(title="Real Estate Agent API", version="1.0.0")

# Security setup
security = HTTPBearer()
API_KEYS = os.getenv("API_KEY", "").split(",")  # Comma-separated list of valid API keys

# OAuth2 settings - use a separate secret for OAuth2
OAUTH2_SECRET = os.getenv("OAUTH2_SECRET", "oauth2-secret-key-for-vapi")

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

def verify_oauth2_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify OAuth2 token from Authorization header"""
    try:
        token = credentials.credentials
        # Decode and verify the JWT token
        payload = jwt.decode(token, OAUTH2_SECRET, algorithms=["HS256"])
        return payload.get("sub", "unknown")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_hybrid_auth(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify either API key or OAuth2 token"""
    token = credentials.credentials
    
    # First try API key
    if token in API_KEYS:
        return "api_key"
    
    # Then try OAuth2 token
    try:
        payload = jwt.decode(token, OAUTH2_SECRET, algorithms=["HS256"])
        return payload.get("sub", "unknown")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid API key or token")

# OAuth2 endpoints for VAPI
@app.post("/oauth/token")
async def oauth_token(
    grant_type: str = Form("client_credentials"),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None)
):
    """OAuth2 token endpoint for VAPI authentication"""
    # Debug logging
    print(f"OAuth2 request received:")
    print(f"  grant_type: {grant_type}")
    print(f"  client_id: {client_id}")
    print(f"  client_secret: {client_secret[:20]}..." if client_secret else "None")
    print(f"  Available API_KEYS: {[key[:20] + '...' for key in API_KEYS]}")
    
    # Simple OAuth2 implementation - in production, use proper OAuth2 library
    if grant_type == "client_credentials":
        # For VAPI, we'll accept the OAuth2 secret as client credentials
        if client_secret and client_secret == OAUTH2_SECRET:
            # Generate a JWT token
            payload = {
                "sub": client_id or "vapi-client",
                "exp": time.time() + 3600,  # 1 hour expiration
                "iat": time.time(),
                "scope": "chat"
            }
            token = jwt.encode(payload, OAUTH2_SECRET, algorithm="HS256")
            
            print(f"OAuth2 token generated successfully for client: {client_id}")
            return {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "chat"
            }
        else:
            # Debug: print what we received vs what we expect
            print(f"OAuth2 authentication failed:")
            print(f"  client_secret provided: {bool(client_secret)}")
            print(f"  client_secret in API_KEYS: {client_secret in API_KEYS if client_secret else False}")
            raise HTTPException(status_code=401, detail="Invalid client credentials")
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")

@app.get("/oauth/token")
async def oauth_token_info():
    """OAuth2 token info endpoint"""
    return {
        "issuer": "real-estate-agent",
        "authorization_endpoint": "/oauth/authorize",
        "token_endpoint": "/oauth/token",
        "scopes_supported": ["chat"]
    }

@app.get("/.well-known/oauth-authorization-server")
async def oauth_discovery():
    """OAuth2 discovery endpoint for VAPI"""
    return {
        "issuer": "https://web-production-dd65f.up.railway.app",
        "authorization_endpoint": "https://web-production-dd65f.up.railway.app/oauth/authorize",
        "token_endpoint": "https://web-production-dd65f.up.railway.app/oauth/token",
        "token_introspection_endpoint": "https://web-production-dd65f.up.railway.app/oauth/introspect",
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "grant_types_supported": ["client_credentials"],
        "scopes_supported": ["chat"],
        "response_types_supported": ["token"],
        "introspection_endpoint_auth_methods_supported": ["client_secret_post"]
    }

@app.get("/oauth/authorize")
async def oauth_authorize():
    """OAuth2 authorization endpoint (placeholder)"""
    return {"message": "Authorization endpoint - not implemented for this use case"}

@app.post("/oauth/introspect")
async def oauth_introspect(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None)
):
    """OAuth2 token introspection endpoint (RFC 7662)"""
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(token, OAUTH2_SECRET, algorithms=["HS256"])
        
        # Check if token is expired
        current_time = time.time()
        if payload.get("exp", 0) < current_time:
            return {
                "active": False,
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "scope": payload.get("scope"),
                "sub": payload.get("sub")
            }
        
        return {
            "active": True,
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
            "scope": payload.get("scope"),
            "sub": payload.get("sub"),
            "client_id": payload.get("sub")
        }
    except jwt.InvalidTokenError:
        return {"active": False}

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

# OpenAI-compatible endpoint for VAPI
@app.post("/chat/completions")
async def chat_completions(
    request: dict,
    auth: str = Depends(verify_hybrid_auth)
):
    """OpenAI-compatible chat completions endpoint for VAPI"""
    try:
        # Extract messages from VAPI request
        messages = request.get("messages", [])
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Convert OpenAI format to our format
        conversation_messages = []
        for msg in messages:
            if msg.get("role") == "user":
                conversation_messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                conversation_messages.append(AIMessage(content=msg.get("content", "")))
        
        # Create state for the graph
        state = State(messages=conversation_messages)
        
        # Run the graph
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = graph.invoke(state, config=config)
        
        # Extract AI response
        ai_message = result["messages"][-1]
        
        # Format response in OpenAI-compatible format
        response = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "real-estate-agent",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": ai_message.content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(ai_message.content),
                "total_tokens": len(str(messages)) + len(ai_message.content)
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion error: {str(e)}")

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

@app.get("/langgraph")
async def langgraph_info():
    """LangGraph Studio endpoint - exposes graph structure and metadata"""
    return {
        "name": "real-estate-agent",
        "version": "1.0.0",
        "description": "Real Estate Agent Chatbot using LangGraph",
        "graph": {
            "nodes": [
                {
                    "name": "chatbot",
                    "type": "llm",
                    "config": {
                        "model": "gpt-4o-mini",
                        "temperature": 0
                    }
                }
            ],
            "edges": [
                {
                    "from": "START",
                    "to": "chatbot"
                },
                {
                    "from": "chatbot", 
                    "to": "END"
                }
            ]
        },
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "sessions": "/sessions/{session_id}",
            "langgraph": "/langgraph"
        },
        "authentication": {
            "type": "bearer",
            "header": "Authorization"
        }
    }

@app.post("/langgraph/invoke")
async def langgraph_invoke(
    request: dict,
    api_key: str = Depends(verify_api_key)
):
    """LangGraph Studio invoke endpoint - direct graph execution"""
    try:
        # Extract the input from LangGraph Studio format
        messages = request.get("messages", [])
        config = request.get("config", {})
        
        # Convert to our format
        if messages:
            # Get the last human message
            last_message = messages[-1]
            if isinstance(last_message, dict) and last_message.get("type") == "human":
                user_message = last_message.get("content", "")
                
                # Create our chat request format
                chat_request = ChatRequest(
                    message=user_message,
                    session_id=config.get("thread_id", str(uuid.uuid4()))
                )
                
                # Use our existing chat logic
                result = await chat_endpoint(chat_request, api_key)
                return result
        
        return {"error": "Invalid request format"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangGraph invoke error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)