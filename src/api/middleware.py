from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_config


def setup_cors_middleware(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application."""
    try:
        config = get_config()
        cors_settings = config.server.cors
        
        # Add CORS middleware with settings from config
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_settings.allow_origins,
            allow_credentials=cors_settings.allow_credentials,
            allow_methods=cors_settings.allow_methods,
            allow_headers=cors_settings.allow_headers,
        )
    except Exception:
        # Fallback CORS configuration if settings fail to load
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the FastAPI application."""
    setup_cors_middleware(app)