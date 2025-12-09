from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form, Header
import logging
from .video_generation import video_generation_service
from .video_generation_schema import (
    VideoGenerationRequest, 
    VideoGenerationResponse,
    VideoModel,
    TEXT_TO_VIDEO_MODELS,
    IMAGE_TO_VIDEO_MODELS,
    VideoMode,
    VideoShape
)
from ...core.error_handlers import handle_service_error, validate_file_types

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    mode: str = Form(..., description="Mode: 'generate' or 'edit'"),
    prompt: str = Form(..., description="Text prompt for video generation"),
    model: str = Form(..., description="Exact model name (case-sensitive): veo-2 | veo-3-fast | pixverse | kling | pixverse-image-to-video | kling-image-to-video | wan-2.2"),
    shape: str = Query("landscape", description="Shape: square | portrait | landscape"),
    image_file: UploadFile = File(None, description="Image file (required for image-to-video models). Formats: image/jpeg, image/png, image/webp"),
    user_id: str = Header(None)
):
    """
    Generate videos using various AI models
    
    **IMPORTANT: Use exact model names (case-sensitive)**
    
    **Text-to-Video Models (mode='generate'):**
    - `veo-2` - Google Veo 2.0
    - `veo-3-fast` - Google Veo 3.0 Fast
    - `pixverse` - Pixverse Text-to-Video
    - `kling` - Kling Text-to-Video
    
    **Image-to-Video Models (mode='edit'):**
    - `pixverse-image-to-video` - Pixverse Image-to-Video (**requires 1 image file**)
    - `kling-image-to-video` - Kling Image-to-Video (**requires 1 image file**)
    - `wan-2.2` - WAN 2.2 Image-to-Video (**requires 1 image file**)
    
    **Image Requirements (edit mode only):**
    - Supported formats: image/jpeg, image/png, image/webp
    - Exactly 1 image file required for image-to-video
    """
    try:
        # Validate mode
        if mode not in [m.value for m in VideoMode]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": "Mode must be 'generate' or 'edit'"}
            )
        
        # Validate model based on mode
        if mode == "generate":
            valid_models = [m.value for m in TEXT_TO_VIDEO_MODELS]
            if model not in valid_models:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Validation Error", "message": f"Invalid model for generate mode. Valid models: {', '.join(valid_models)}"}
                )
        else:  # edit mode
            valid_models = [m.value for m in IMAGE_TO_VIDEO_MODELS]
            if model not in valid_models:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Validation Error", "message": f"Invalid model for edit mode. Valid models: {', '.join(valid_models)}"}
                )
        
        # Validate shape
        if shape not in [s.value for s in VideoShape]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": f"Invalid shape. Valid shapes: {', '.join([s.value for s in VideoShape])}"}
            )

        # Validate prompt
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": "Prompt is required"}
            )

        # For edit mode, validate image file
        image_bytes = None
        image_filename = None
        if mode == "edit":
            if not image_file or not image_file.filename:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Validation Error", "message": "Image file required for edit mode"}
                )
            # Validate file type
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            validate_file_types([image_file], allowed_types, "image_file")
            # Read file bytes
            image_bytes = await image_file.read()
            image_filename = image_file.filename

        # Generate the video
        video_url = await video_generation_service.generate_video(
            prompt=prompt,
            model=model,
            mode=mode,
            user_id=user_id,
            shape=shape,
            image_file=image_bytes,
            image_filename=image_filename
        )

        success_message = f"Video {'generated' if mode == 'generate' else 'created from image'} successfully using {model}"

        return VideoGenerationResponse(
            status=200,
            success_message=success_message,
            video_url=video_url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in video generation: {str(e)}")
        raise handle_service_error(e, model, "video generation")
