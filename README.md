# Real Estate Agent Chatbot

A FastAPI-based chatbot using LangGraph and OpenAI for real estate assistance.

## Features

- 🤖 AI-powered real estate agent chatbot
- 💬 Session-based conversations
- 🌐 RESTful API endpoints
- 📞 VAPI webhook support for voice integration
- 🔒 Session management and history
- 🏥 Health check endpoints

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   Create a `.env` file with the following variables:
   ```
   # OpenAI API Key
   OPENAI_API_KEY=your_openai_api_key_here
   
   # API Key for FastAPI authentication
   API_KEY=your_api_key_here
   
   # LangSmith Configuration (optional but recommended)
   LANGCHAIN_API_KEY=your_langsmith_api_key_here
   LANGCHAIN_PROJECT=real-estate-agent
   ```

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Chat Endpoint
- **POST** `/chat`
- Send messages to the chatbot
- **Authentication Required**: Bearer token in Authorization header
- Request headers:
  ```
  Authorization: Bearer your_api_key_here
  ```
- Request body:
  ```json
  {
    "message": "Hello! I'm looking for a house.",
    "session_id": "optional-session-id"
  }
  ```

### VAPI Webhook
- **POST** `/vapi/webhook`
- For voice integration with VAPI
- Request body:
  ```json
  {
    "session_id": "session-id",
    "user_message": "Hello",
    "context": {}
  }
  ```

### Session Management
- **GET** `/sessions/{session_id}` - Get conversation history (Authentication Required)
- **DELETE** `/sessions/{session_id}` - Delete a session (Authentication Required)

### Health Check
- **GET** `/health` - Check API status

## API Documentation

Once running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Testing

Run the test script to verify the API:
```bash
python test_api.py
```

## Deployment

### Local Development
The app is ready to run locally with the provided setup.

### Production Deployment
For production deployment, consider:
1. Using a production ASGI server like Gunicorn
2. Implementing proper session storage (Redis/Database)
3. Adding authentication and rate limiting
4. Setting up proper logging and monitoring

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Next Steps

1. **Enhance the chatbot** with real estate-specific tools and knowledge
2. **Add database integration** for persistent session storage
3. **Implement authentication** for secure access
4. **Add real estate data sources** and APIs
5. **Create a web interface** for easier interaction

## Architecture

- **FastAPI**: Web framework for the API
- **LangGraph**: Conversation flow management
- **OpenAI GPT-4**: AI language model
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the application
