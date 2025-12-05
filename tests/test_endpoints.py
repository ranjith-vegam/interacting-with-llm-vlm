from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, ANY, AsyncMock
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

# Mock llm_wrapper and other dependencies before importing app
sys.modules["llm_wrapper"] = MagicMock()
sys.modules["src.helper.loggers"] = MagicMock()

# Create async generator mocks
async def async_text_stream():
    for chunk in ["Mocked ", "stream ", "response"]:
        yield chunk

async def async_image_stream():
    for chunk in ["Mocked ", "image ", "stream"]:
        yield chunk

# Mock the services
with patch("src.services.text_model.TextModel") as MockTextModel, \
     patch("src.services.image_model.ImageModel") as MockImageModel:
    
    # Setup mock instances
    mock_text_instance = MockTextModel.return_value
    mock_text_instance.generate_response.return_value = "Mocked text response"
    mock_text_instance.generate_response_stream = AsyncMock(return_value=async_text_stream())
    
    mock_image_instance = MockImageModel.return_value
    mock_image_instance.generate_response.return_value = "Mocked image description"
    mock_image_instance.generate_response_stream = AsyncMock(return_value=async_image_stream())

    # Import app after mocking
    from src.api.router import app
    
    client = TestClient(app)

    def test_text_endpoint_with_all_params():
        print("Testing POST /text_model/chat/completion with all params...")
        response = client.post(
            "/text_model/chat/completion",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.3,
                "seed": 42
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        
        # Verify all params were passed to service
        mock_text_instance.generate_response.assert_called_with(
            ANY, 
            {
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.3,
                "seed": 42,
                "response_format": None
            }
        )
        print("Text endpoint with all params passed!\n")

    def test_text_stream_endpoint():
        print("Testing POST /text_model/chat/stream...")
        # Reset the mock to return a fresh async generator
        mock_text_instance.generate_response_stream = AsyncMock(return_value=async_text_stream())
        
        response = client.post(
            "/text_model/chat/stream",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.5,
                "max_tokens": 512
            }
        )
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        print("Text stream endpoint passed!\n")

    def test_image_endpoint_with_params():
        print("Testing POST /image_model/chat/completion with params...")
        with open("test_image.jpg", "wb") as f:
            f.write(b"fake image content")
            
        try:
            with open("test_image.jpg", "rb") as f:
                response = client.post(
                    "/image_model/chat/completion",
                    files={"image": ("test_image.jpg", f, "image/jpeg")},
                    data={
                        "prompt": "Describe this",
                        "temperature": 0.8,
                        "max_tokens": 256,
                        "seed": 123
                    }
                )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            print("Image endpoint with params passed!\n")
        finally:
            if os.path.exists("test_image.jpg"):
                os.remove("test_image.jpg")

    def test_default_params():
        print("Testing endpoints with default params (no params provided)...")
        response = client.post(
            "/text_model/chat/completion",
            json={"messages": [{"role": "user", "content": "Test"}]}
        )
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        
        # Verify None values were passed (will use defaults from .env)
        mock_text_instance.generate_response.assert_called_with(
            ANY,
            {
                "temperature": None,
                "max_tokens": None,
                "top_p": None,
                "frequency_penalty": None,
                "presence_penalty": None,
                "seed": None,
                "response_format": None
            }
        )
        print("Default params test passed!\n")

    if __name__ == "__main__":
        try:
            test_text_endpoint_with_all_params()
            test_text_stream_endpoint()
            test_image_endpoint_with_params()
            test_default_params()
            print("All tests passed successfully!")
        except Exception as e:
            print(f"Tests failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
