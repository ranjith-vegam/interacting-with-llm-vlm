from llm_wrapper import llm_chat_async, llm_streaming_chat
from src.helper.loggers import text_model_logger
from src.config.settings import get_config
from typing import AsyncGenerator, Optional, Dict, Any

class TextModel:
    def __init__(self):
        self.settings = get_config().text_model
    
    def _merge_args(self, override_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge default settings with override arguments."""
        default_args = self.settings.llm_args.model_dump(exclude_none=True)
        if override_args:
            # Filter out None values from override_args
            clean_overrides = {k: v for k, v in override_args.items() if v is not None}
            default_args.update(clean_overrides)
        return default_args

    async def generate_response(self, messages, llm_args: Optional[Dict[str, Any]] = None):
        """
        Generate response from LLM using llm_chat_async.
        """
        try:
            merged_args = self._merge_args(llm_args)
            response = await llm_chat_async(
                base_url=self.settings.base_url,
                model_name=self.settings.model_name,
                messages_list=messages,
                max_concurrency=self.settings.max_concurrency,
                args=merged_args,
                logger=text_model_logger
            )
            # llm_chat_async returns a list of responses, get the first one
            return response[0].response if response else ""
        except Exception as e:
            text_model_logger.error(f"Error in generate_response: {str(e)}")
            raise

    async def generate_response_stream(self, messages, llm_args: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """
        Stream responses from LLM using llm_streaming_chat.
        Returns an async generator that yields text chunks.
        """
        try:
            merged_args = self._merge_args(llm_args)
            
            # Use llm_streaming_chat from llm_wrapper
            async for chunk in llm_streaming_chat(
                base_url=self.settings.base_url,
                model_name=self.settings.model_name,
                messages=messages,
                api_key='',
                timeout=None,
                max_retries=3,
                args=merged_args,
                logger=text_model_logger
            ):
                yield chunk

        except Exception as e:
            text_model_logger.error(f"Error in generate_response_stream: {str(e)}")
            yield f"Error: {str(e)}"