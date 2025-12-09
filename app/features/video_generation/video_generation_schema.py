from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Define all available video models
class VideoModel(str, Enum):
    # Text-to-Video Models
    VEO_2 = "veo-2"
    VEO_3_FAST = "veo-3-fast"
    PIXVERSE = "pixverse"
    KLING = "kling"
    
    # Image-to-Video Models
    PIXVERSE_IMAGE_TO_VIDEO = "pixverse-image-to-video"
    KLING_IMAGE_TO_VIDEO = "kling-image-to-video"
    WAN_2_2 = "wan-2.2"

class VideoShape(str, Enum):
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class VideoMode(str, Enum):
    GENERATE = "generate"
    EDIT = "edit"

# Model capabilities mapping
TEXT_TO_VIDEO_MODELS = [
    VideoModel.VEO_2,
    VideoModel.VEO_3_FAST,
    VideoModel.PIXVERSE,
    VideoModel.KLING
]

IMAGE_TO_VIDEO_MODELS = [
    VideoModel.PIXVERSE_IMAGE_TO_VIDEO,
    VideoModel.KLING_IMAGE_TO_VIDEO,
    VideoModel.WAN_2_2
]

class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for video generation")
    model: str = Field(..., description="Exact model name (case-sensitive)")
    mode: str = Field(..., description="Mode: 'generate' for text-to-video, 'edit' for image-to-video")
    shape: str = Field("landscape", description="Video shape: square, portrait, landscape")

class VideoGenerationResponse(BaseModel):
    status: int
    success_message: str
    video_url: str
