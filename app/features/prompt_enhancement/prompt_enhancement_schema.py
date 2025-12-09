from pydantic import BaseModel, Field
from typing import Optional

class PromptEnhancementRequest(BaseModel):
    prompt: str = Field(..., description="Original prompt to enhance")
    type: str = Field("image", description="Type of content: image, video, audio")

class PromptEnhancementResponse(BaseModel):
    status: int
    success_message: str
    enhanced_prompt: str
