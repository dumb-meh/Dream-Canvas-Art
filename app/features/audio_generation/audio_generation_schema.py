from pydantic import BaseModel, Field
from typing import Optional

class AudioGenerationRequest(BaseModel):
    verse_prompt: str = Field(..., description="Verse prompt for music generation")
    lyrics_prompt: Optional[str] = Field(None, description="Optional lyrics prompt")

class AudioGenerationResponse(BaseModel):
    status: int
    success_message: str
    audio_url: str
