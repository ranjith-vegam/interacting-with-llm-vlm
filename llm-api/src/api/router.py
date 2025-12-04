from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_config

config = get_config()

# Initialize FastAPI with OpenAPI configuration for API key
app = FastAPI(
    title="LLM API",
    description="REST API for interacting with Large Language Models (LLMs) and Visual Language Models (VLMs)",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "LLM Inference",
            "description": "Endpoints for text and image model inference"
        }
    ]
)

# Add security scheme to OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter your API key here. Get it from your .env file (API_KEY variable)."
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server.cors.allow_origins,
    allow_credentials=config.server.cors.allow_credentials,
    allow_methods=config.server.cors.allow_methods,
    allow_headers=config.server.cors.allow_headers,
)

# Include routers
from src.api.routes.model_inference_endpoints import router as model_router
app.include_router(model_router)
