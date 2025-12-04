# LLM API

A FastAPI-based REST API for interacting with Large Language Models (LLMs) and Visual Language Models (VLMs).

## Features

- **Text Generation**: Generate text responses from conversational prompts
- **Image Analysis**: Analyze images and answer questions about them
- **Streaming Support**: Real-time streaming responses for both text and image models
- **Flexible Parameters**: Control model behavior with temperature, max_tokens, and more
- **API Key Authentication**: Secure your API with API key authentication
- **User-Friendly**: Comprehensive API documentation for users unfamiliar with LLMs

## Quick Start

### Installation

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your model endpoints and API key
```

### Running the Server

```bash
# Using uv
uv run main.py

# Or with Python
python main.py
```

The API will be available at `http://localhost:1999` (or your configured port).

## Authentication

All API endpoints require an API key for authentication. Include the API key in the request header:

```bash
-H "X-API-Key: your-secret-api-key-here"
```

Set your API key in the `.env` file:
```bash
API_KEY="your-secret-api-key-here"
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:1999/docs`
- ReDoc: `http://localhost:1999/redoc`

## Endpoints

### Text Model

#### Generate Text Response
**POST** `/text_model/chat/completion`

Generate a text response based on conversation messages.

**Example Request:**
```bash
curl -X POST "http://localhost:1999/text_model/chat/completion" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-api-key-here" \
     -d '{
           "messages": [
             {"role": "user", "content": "What is the capital of France?"}
           ],
           "temperature": 0.7,
           "max_tokens": 100
         }'
```

**Example Response:**
```json
{
  "response": "The capital of France is Paris."
}
```

#### Stream Text Response
**POST** `/text_model/chat/stream`

Stream the text response in real-time.

**Example Request:**
```bash
curl -N -X POST "http://localhost:1999/text_model/chat/stream" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-api-key-here" \
     -d '{
           "messages": [
             {"role": "user", "content": "Tell me a short story"}
           ],
           "temperature": 0.8
         }'
```

### Image Model

#### Analyze Image
**POST** `/image_model/chat/completion`

Upload an image and get a description or answer.

**Example Request:**
```bash
curl -X POST "http://localhost:1999/image_model/chat/completion" \
     -H "X-API-Key: your-secret-api-key-here" \
     -F "image=@photo.jpg" \
     -F "prompt=What objects are in this image?" \
     -F "temperature=0.3"
```

**Example Response:**
```json
{
  "response": "The image contains a laptop, coffee mug, and notebook on a wooden desk."
}
```

#### Stream Image Analysis
**POST** `/image_model/chat/stream`

Stream the image analysis response in real-time.

## Parameters

All endpoints support the following optional parameters:

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `temperature` | float | 0.0-2.0 | 0.0 | Controls randomness. Lower = focused, Higher = creative |
| `max_tokens` | int | >0 | 2048 | Maximum response length in tokens |
| `top_p` | float | 0.0-1.0 | 1.0 | Controls diversity via nucleus sampling |
| `frequency_penalty` | float | -2.0 to 2.0 | 0.0 | Reduces word/phrase repetition |
| `presence_penalty` | float | -2.0 to 2.0 | 0.0 | Encourages new topics |
| `seed` | int | any | 0 | For reproducible outputs |
| `response_format` | dict | - | See below | Output format specification |

### Response Format Examples

#### Default JSON Object Format
```json
{
  "messages": [{"role": "user", "content": "Hello"}],
  "response_format": {"type": "json_object"}
}
```

This tells the model to return valid JSON.

#### Custom Structured Format
```json
{
  "messages": [{"role": "user", "content": "Analyze this product review"}],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "product_review",
      "schema": {
        "type": "object",
        "properties": {
          "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
          "rating": {"type": "integer", "minimum": 1, "maximum": 5},
          "summary": {"type": "string"}
        },
        "required": ["sentiment", "rating", "summary"]
      }
    }
  }
}
```

This ensures the response follows your exact schema.

#### Text Format (No JSON)
```json
{
  "messages": [{"role": "user", "content": "Write a poem"}],
  "response_format": {"type": "text"}
}
```

For plain text responses without JSON formatting.

## Configuration

Edit `.env` to configure:

```bash
# Server settings
SERVER__PORT=1999

# API Authentication
API_KEY="your-secret-api-key-here"

# Text Model
TEXT_MODEL__MODEL_NAME="your-model-name"
TEXT_MODEL__BASE_URL="http://your-llm-endpoint"
TEXT_MODEL__MAX_CONCURRENCY=10
TEXT_MODEL__LLM_ARGS__TEMPERATURE=0
TEXT_MODEL__LLM_ARGS__MAX_TOKENS=2048

# Image Model
IMAGE_MODEL__MODEL_NAME="your-vlm-name"
IMAGE_MODEL__BASE_URL="http://your-vlm-endpoint"
IMAGE_MODEL__MAX_CONCURRENCY=10
```

## Security

- **API Key Authentication**: All endpoints are protected with API key authentication
- **Header-based**: API key is passed via `X-API-Key` header
- **Environment Variable**: Store your API key securely in `.env` file
- **Never commit**: Add `.env` to `.gitignore` to prevent accidental commits

## Advanced Usage

### Multi-turn Conversation
```json
{
  "messages": [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "What are its main features?"}
  ]
}
```

### Creative Writing
```json
{
  "messages": [{"role": "user", "content": "Write a creative story"}],
  "temperature": 1.5,
  "frequency_penalty": 0.5,
  "presence_penalty": 0.6
}
```

### Deterministic Responses
```json
{
  "messages": [{"role": "user", "content": "Calculate 2+2"}],
  "temperature": 0.0,
  "seed": 42
}
```

## Testing

```bash
# Run tests
uv run tests/test_endpoints.py
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Missing API Key. Please provide X-API-Key header."
}
```

### 403 Forbidden
```json
{
  "detail": "Invalid API Key"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing what went wrong"
}
```

## License

[Your License Here]
