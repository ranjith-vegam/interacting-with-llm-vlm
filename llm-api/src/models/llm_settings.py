from pydantic import BaseModel, field_validator
from typing import Optional
import json

# Reusable LLMArgs model
class LLMArgs(BaseModel):
    temperature: Optional[float] = None
    seed: Optional[int] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    response_format: Optional[dict] = None

    @field_validator("response_format", mode="before")
    def parse_response_format(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

class TextModelSettings(BaseModel):
    model_name: str
    base_url: str  
    max_concurrency: int = 10
    llm_args: LLMArgs

class ImageModelSettings(BaseModel):
    model_name: str
    base_url: str
    max_concurrency: int = 10
    llm_args: LLMArgs
