from llm_wrapper import llm_chat_async, llm_streaming_chat
from src.helper.loggers import image_model_logger
from src.config.settings import get_config
from typing import AsyncGenerator, Optional, Dict, Any
import base64

class ImageModel:
    def __init__(self):
        self.settings = get_config().image_model
    
    def _merge_args(self, override_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge default settings with override arguments."""
        default_args = self.settings.llm_args.model_dump(exclude_none=True)
        if override_args:
            clean_overrides = {k: v for k, v in override_args.items() if v is not None}
            default_args.update(clean_overrides)
        return default_args
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_image_messages(self, image_path: str, prompt: str) -> list:
        """Create messages list with image for VLM."""
        # Encode image to base64
        base64_image = self._encode_image(image_path)
        
        # Determine image type from file extension
        import os
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')
        
        # Create message with image content
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        return messages
    
    async def generate_response(self, image_path: str, prompt: str, llm_args: Optional[Dict[str, Any]] = None):
        """
        Generate response from VLM using llm_chat_async.
        """
        try:
            merged_args = self._merge_args(llm_args)
            messages = self._create_image_messages(image_path, prompt)
            
            response = await llm_chat_async(
                base_url=self.settings.base_url,
                model_name=self.settings.model_name,
                messages_list=messages,
                max_concurrency=self.settings.max_concurrency,
                args=merged_args,
                logger=image_model_logger
            )
            # llm_chat_async returns a list of responses, get the first one
            return response[0].response if response else ""
        except Exception as e:
            image_model_logger.error(f"Error in generate_response: {str(e)}")
            raise

    async def generate_response_stream(self, image_path: str, prompt: str, llm_args: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """
        Stream responses from VLM using llm_streaming_chat.
        Returns an async generator that yields text chunks.
        """
        try:
            merged_args = self._merge_args(llm_args)
            messages = self._create_image_messages(image_path, prompt)
            
            async for chunk in llm_streaming_chat(
                base_url=self.settings.base_url,
                model_name=self.settings.model_name,
                messages=messages,
                api_key='',
                timeout=None,
                max_retries=3,
                args=merged_args,
                logger=image_model_logger
            ):
                yield chunk

        except Exception as e:
            image_model_logger.error(f"Error in generate_response_stream: {str(e)}")
            yield f"Error: {str(e)}"
