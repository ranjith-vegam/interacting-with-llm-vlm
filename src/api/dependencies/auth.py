from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.config.settings import get_config

# Define the API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify the API key from the request header.
    
    Args:
        api_key: The API key from the X-API-Key header
        
    Raises:
        HTTPException: If the API key is missing or invalid
        
    Returns:
        str: The validated API key
    """
    config = get_config()
    
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide X-API-Key header."
        )
    
    if api_key != config.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key
