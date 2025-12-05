from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, Json
from typing import List, Dict, Any, Generator, Optional
import shutil
import os
import uuid

from src.services.text_model import TextModel
from src.services.image_model import ImageModel
from src.api.dependencies.auth import verify_api_key

router = APIRouter(tags=["LLM Inference"], dependencies=[Depends(verify_api_key)])

# Initialize services
text_model_service = TextModel()
image_model_service = ImageModel()

class Message(BaseModel):
    role: str = Field(
        ..., 
        description="The role of the message sender. Use 'user' for your messages and 'assistant' for AI responses.",
        examples=["user", "assistant"]
    )
    content: str = Field(
        ..., 
        description="The actual text content of the message.",
        examples=["Hello, how are you?"]
    )

class TextRequest(BaseModel):
    messages: List[Message] = Field(
        ..., 
        description="A list of conversation messages. Include previous messages for context."
    )
    temperature: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Controls randomness in responses. Lower values (0.0-0.5) make output more focused and deterministic. Higher values (0.5-2.0) make it more creative and varied. Default is set in configuration.",
        examples=[0.0]
    )
    max_tokens: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum length of the response in tokens (roughly 4 characters per token). Limits how long the AI's answer can be. Default is set in configuration.",
        examples=[256]
    )
    top_p: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Controls diversity via nucleus sampling. Lower values make responses more focused, higher values more diverse. Alternative to temperature. Default is set in configuration.",
        examples=[1.0]
    )
    frequency_penalty: Optional[float] = Field(
        None,
        ge=-2.0,
        le=2.0,
        description="Reduces repetition of words/phrases. Positive values discourage repetition, negative values encourage it. Range: -2.0 to 2.0. Default is set in configuration.",
        examples=[0.0]
    )
    presence_penalty: Optional[float] = Field(
        None,
        ge=-2.0,
        le=2.0,
        description="Encourages talking about new topics. Positive values make the AI more likely to introduce new subjects. Range: -2.0 to 2.0. Default is set in configuration.",
        examples=[0.0]
    )
    seed: Optional[int] = Field(
        None, 
        description="A number to make responses reproducible. Using the same seed with the same input will give the same output. Useful for testing. Default is set in configuration.",
        examples=[42]
    )
    response_format: Optional[Dict[str, Any]] = Field(
        None, 
        description="Specify the format of the response. Examples: {'type': 'json_object'} for JSON, {'type': 'text'} for plain text, or use json_schema for structured output. Default is set in configuration.",
        examples=[
            {"type": "text"},
            {"type": "json_object"},
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    }
                }
            }
        ]
    )

class TextResponse(BaseModel):
    response: str = Field(..., description="The AI-generated text response")

class ImageResponse(BaseModel):
    response: str = Field(..., description="The AI-generated description or answer about the image")

# Text Model Endpoints

@router.post(
    "/text_model/chat/completion",
    response_model=TextResponse,
    summary="Generate Text Response",
    description="""Generate an AI text response based on your conversation messages.

How to use:
- Send a list of messages with roles ('user' or 'assistant')
- The AI will respond based on the conversation context
- Optionally adjust parameters to control the response style

**Example with curl:**
```bash
curl -X POST "http://localhost:1999/text_model/chat/completion" \\
     -H "Content-Type: application/json" \\
     -H "X-API-Key: your-secret-api-key-here" \\
     -d '{
       "messages": [
         {"role": "user", "content": "What is the capital of France?"}
       ],
       "temperature": 0.7,
       "max_tokens": 100
     }'
```

**Example with response_format:**
```bash
# For JSON response
curl -X POST "http://localhost:1999/text_model/chat/completion" \\
     -H "Content-Type: application/json" \\
     -H "X-API-Key: your-secret-api-key-here" \\
     -d '{
       "messages": [{"role": "user", "content": "List 3 colors"}],
       "response_format": {"type": "json_object"}
     }'
```

Common use cases:
- Chatbots and conversational AI
- Question answering
- Text generation and completion
- Creative writing assistance
    """,
    response_description="The AI-generated text response based on your input."
)
async def generate_text(request: TextRequest):
    try:
        # Convert Pydantic models to dicts for the service
        messages = [m.model_dump() for m in request.messages]
        llm_args = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "seed": request.seed,
            "response_format": request.response_format
        }
        
        # Await the async generate_response method
        response = await text_model_service.generate_response(messages, llm_args)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/text_model/chat/stream",
    summary="Stream Text Response",
    description="""Stream the AI text response token by token in real-time.

How to use:
- Same as the completion endpoint, but responses arrive progressively
- Ideal for showing typing indicators or real-time responses
- Use Server-Sent Events (SSE) to receive the stream

**Example with curl:**
```bash
curl -N -X POST "http://localhost:1999/text_model/chat/stream" \\
     -H "Content-Type: application/json" \\
     -H "X-API-Key: your-secret-api-key-here" \\
     -d '{
       "messages": [
         {"role": "user", "content": "Tell me a short story"}
       ],
       "temperature": 0.8,
       "max_tokens": 200
     }'
```

Note: The `-N` flag disables buffering so you can see the stream in real-time.

Common use cases:
- Real-time chat interfaces
- Progressive content generation
- Live typing effects
    """,
    response_description="A stream of text tokens that form the complete response."
)
async def stream_text(request: TextRequest):
    try:
        messages = [m.model_dump() for m in request.messages]
        llm_args = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "seed": request.seed,
            "response_format": request.response_format
        }
        
        async def generate():
            async for chunk in text_model_service.generate_response_stream(messages, llm_args):
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image Model Endpoints

@router.post(
    "/image_model/chat/completion",
    response_model=ImageResponse,
    summary="Analyze Image",
    description="""Upload an image and get an AI-generated description or answer to your question about it.

How to use:
- Upload an image file (JPEG, PNG, etc.)
- Provide a prompt/question about the image
- Optionally adjust parameters to control the response style

**Example with curl:**
```bash
curl -X POST "http://localhost:1999/image_model/chat/completion" \\
     -H "X-API-Key: your-secret-api-key-here" \\
     -F "image=@/path/to/your/image.jpg" \\
     -F "prompt=What objects are in this image?" \\
     -F "temperature=0.3" \\
     -F "max_tokens=100"
```

**Example for detailed analysis:**
```bash
curl -X POST "http://localhost:1999/image_model/chat/completion" \\
     -H "X-API-Key: your-secret-api-key-here" \\
     -F "image=@photo.jpg" \\
     -F "prompt=Describe this image in detail, including colors, objects, and setting"
```

Common use cases:
- Image captioning and description
- Visual question answering
- Object detection and recognition
- Scene understanding
    """,
    response_description="The AI-generated text describing or answering about the image."
)
async def generate_image_description(
    image: UploadFile = File(..., description="The image file to analyze (JPEG, PNG, etc.)"),
    prompt: str = Form("Describe this image", description="Your question or instruction about the image"),
    temperature: Optional[float] = Form(None, ge=0.0, le=1.0, description="Controls creativity (0.0-2.0). Lower = focused, Higher = creative.", examples=[0.0]),
    max_tokens: Optional[int] = Form(None, gt=0, description="Maximum response length in tokens.", examples=[256]),
    top_p: Optional[float] = Form(None, ge=0.0, le=1.0, description="Controls diversity (0.0-1.0).", examples=[1.0]),
    frequency_penalty: Optional[float] = Form(None, ge=-2.0, le=2.0, description="Reduces repetition (-2.0 to 2.0).", examples=[0.0]),
    presence_penalty: Optional[float] = Form(None, ge=-2.0, le=2.0, description="Encourages new topics (-2.0 to 2.0).", examples=[0.0]),
    seed: Optional[int] = Form(None, description="Seed for reproducible outputs.", examples=[42]),
    response_format: Optional[Json] = Form(None, description="Response format", examples=[{"type": "text"}])
):
    temp_file_path = None
    try:
        file_extension = os.path.splitext(image.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join("/tmp", temp_filename)
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        llm_args = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "seed": seed,
            "response_format": response_format
        }
        
        # Await the async generate_response method
        response = await image_model_service.generate_response(temp_file_path, prompt, llm_args)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post(
    "/image_model/chat/stream",
    summary="Stream Image Analysis",
    description="""Stream the AI-generated description or answer about an image in real-time.

How to use:
- Upload an image file
- Provide a prompt/question
- Receive the response progressively as it's generated

**Example with curl:**
```bash
curl -N -X POST "http://localhost:1999/image_model/chat/stream" \\
     -H "X-API-Key: your-secret-api-key-here" \\
     -F "image=@/path/to/your/image.jpg" \\
     -F "prompt=Describe this image in detail" \\
     -F "max_tokens=200"
```

Note: The `-N` flag disables buffering for real-time streaming.

Common use cases:
- Real-time image analysis interfaces
- Progressive image captioning
- Live visual question answering
    """,
    response_description="A stream of text tokens describing or answering about the image."
)
async def stream_image_description(
    image: UploadFile = File(..., description="The image file to analyze (JPEG, PNG, etc.)"),
    prompt: str = Form("Describe this image", description="Your question or instruction about the image"),
    temperature: Optional[float] = Form(None, ge=0.0, le=1.0, description="Controls creativity (0.0-2.0).", examples=[0.0]),
    max_tokens: Optional[int] = Form(None, gt=0, description="Maximum response length in tokens.", examples=[256]),
    top_p: Optional[float] = Form(None, ge=0.0, le=1.0, description="Controls diversity (0.0-1.0).", examples=[1.0]),
    frequency_penalty: Optional[float] = Form(None, ge=-2.0, le=2.0, description="Reduces repetition (-2.0 to 2.0).", examples=[0.0]),
    presence_penalty: Optional[float] = Form(None, ge=-2.0, le=2.0, description="Encourages new topics (-2.0 to 2.0).", examples=[0.0]),
    seed: Optional[int] = Form(None, description="Seed for reproducible outputs.", examples=[42]),
    response_format: Optional[Json] = Form(None, description="Response format (e.g., JSON).", examples=[{"type": "text"}])
):
    temp_file_path = None
    try:
        file_extension = os.path.splitext(image.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join("/tmp", temp_filename)
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        llm_args = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "seed": seed,
            "response_format": response_format
        }

        async def iterfile():
            try:
                async for chunk in image_model_service.generate_response_stream(temp_file_path, prompt, llm_args):
                    yield chunk
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return StreamingResponse(
            iterfile(),
            media_type="text/event-stream"
        )
    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
