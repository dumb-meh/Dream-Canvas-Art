from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

# Define all available image models
class ImageModel(str, Enum):
    # Text-to-Image Only Models
    DALLE = "dalle"
    FLUX_1_SPRO = "flux_1_spro"
    GEMINI = "gemini"
    FLUX_KONTEXT_DEV = "flux_kontext_dev"
    QWEN = "qwen"
    
    # Image Edit Only Models
    FLUX_KONTEXT_EDIT = "flux_kontext_edit"
    
    # Models that support BOTH text-to-image AND image editing
    GEMINI_NANOBANANA = "gemini_nanobanana"
    SEEDREAM = "seedream"

class ImageStyle(str, Enum):
    PHOTO = "Photo"
    ILLUSTRATION = "Illustration"
    COMIC = "Comic"
    ANIME = "Anime"
    ABSTRACT = "Abstract"
    FANTASY = "Fantasy"
    POPART = "PopArt"

class ImageShape(str, Enum):
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class ImageMode(str, Enum):
    GENERATE = "generate"
    EDIT = "edit"

# Model capabilities mapping
TEXT_TO_IMAGE_MODELS = [
    ImageModel.DALLE,
    ImageModel.FLUX_1_SPRO,
    ImageModel.GEMINI,
    ImageModel.FLUX_KONTEXT_DEV,
    ImageModel.QWEN,
    ImageModel.GEMINI_NANOBANANA,  # Can do both
    ImageModel.SEEDREAM  # Can do both
]

IMAGE_EDIT_MODELS = [
    ImageModel.FLUX_KONTEXT_EDIT,
    ImageModel.GEMINI_NANOBANANA,  # Can do both
    ImageModel.SEEDREAM  # Can do both
]

# Max reference images per model for edit mode
MODEL_MAX_IMAGES = {
    ImageModel.GEMINI_NANOBANANA: 4,
    ImageModel.FLUX_KONTEXT_EDIT: 1,
    ImageModel.SEEDREAM: 4
}

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    mode: ImageMode = Field(..., description="Mode: 'generate' for text-to-image, 'edit' for image editing")
    style: ImageStyle = Field(ImageStyle.PHOTO, description="Image style")
    shape: ImageShape = Field(ImageShape.SQUARE, description="Image shape")

class ImageGenerationResponse(BaseModel):
    status: int
    success_message: str
    image_url: str
    model_used: str
    shape: str
