from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form, Header
from typing import List, Union, Optional
import logging
from .image_generation import image_generation_service
from .image_generation_schema import (
    ImageGenerationResponse, 
    ImageModel,
    TEXT_TO_IMAGE_MODELS,
    IMAGE_EDIT_MODELS,
    MODEL_MAX_IMAGES,
    ImageMode,
    ImageStyle,
    ImageShape
)
from ...core.error_handlers import handle_service_error, validate_file_types

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
    mode: str = Form(..., description="Mode: 'generate' or 'edit'"),
    prompt: str = Form(..., description="Text prompt for image generation/editing"),
    model: str = Form(..., description="Exact model name (case-sensitive): dalle | flux_1_spro | gemini | flux_kontext_dev | qwen | gemini_nanobanana | seedream | flux_kontext_edit"),
    style: str = Query("Photo", description="Style: Photo | Illustration | Comic | Anime | Abstract | Fantasy | PopArt"),
    shape: str = Query("square", description="Shape: square | portrait | landscape"),
    image_files: Union[List[UploadFile], None] = File(None, description="Reference images (edit mode only). Max 4 files. Required count depends on model: flux_kontext_edit=1, gemini_nanobanana=0-4, seedream=0-4"),
    user_id: str = Header(None)
):
    """
    Generate or edit images using various AI models
    
    **IMPORTANT: Use exact model names (case-sensitive)**
    
    **Text-to-Image Models (mode='generate'):**
    - `dalle` - OpenAI DALL-E 3
    - `flux_1_spro` - Flux 1 SPRO
    - `gemini` - Google Gemini Imagen 4.0
    - `flux_kontext_dev` - Flux Kontext Dev
    - `qwen` - Qwen Image Model
    - `gemini_nanobanana` - Gemini NanoBanana (can also edit with 0-4 reference images)
    - `seedream` - ByteDance SeeDream (can also edit with 0-4 reference images)
    
    **Image Edit Models (mode='edit'):**
    - `flux_kontext_edit` - Flux Kontext Edit (**requires exactly 1 reference image**)
    - `gemini_nanobanana` - Gemini NanoBanana (**supports 0-4 reference images**)
    - `seedream` - ByteDance SeeDream (**supports 0-4 reference images**)
    
    **Image Requirements:**
    - Supported formats: image/jpeg, image/png, image/webp
    - Max 4 files can be uploaded
    - Number of files validated based on selected model
    """
    try:
        # Validate mode
        if mode not in [m.value for m in ImageMode]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": f"Mode must be 'generate' or 'edit'"}
            )

        # Validate model based on mode
        if mode == "generate":
            valid_models = [m.value for m in TEXT_TO_IMAGE_MODELS]
            if model not in valid_models:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Validation Error", "message": f"Invalid model for generate mode. Valid models: {', '.join(valid_models)}"}
                )
        else:  # edit mode
            valid_models = [m.value for m in IMAGE_EDIT_MODELS]
            if model not in valid_models:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Validation Error", "message": f"Invalid model for edit mode. Valid models: {', '.join(valid_models)}"}
                )

        # Validate prompt
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": "Prompt is required"}
            )

        # Validate style
        if style not in [s.value for s in ImageStyle]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": f"Invalid style. Valid styles: {', '.join([s.value for s in ImageStyle])}"}
            )

        # Validate shape
        if shape not in [s.value for s in ImageShape]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": f"Invalid shape. Valid shapes: {', '.join([s.value for s in ImageShape])}"}
            )

        # For edit mode, validate image files
        if mode == "edit":
            if not image_files or not any(f.filename for f in image_files):
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Validation Error", "message": "Image files required for edit mode"}
                )
            
            # Validate file types
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            validate_file_types(image_files, allowed_types, "image_files")
            
            # Validate file count based on model
            file_count = len([f for f in image_files if f.filename])
            
            # Check max 4 files limit
            if file_count > 4:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Validation Error", 
                        "message": f"Maximum 4 image files allowed. You uploaded {file_count} files."
                    }
                )
            
            # Check model-specific requirements
            if model in MODEL_MAX_IMAGES:
                max_allowed = MODEL_MAX_IMAGES[model]
                
                # flux_kontext_edit requires exactly 1 image
                if model == ImageModel.FLUX_KONTEXT_EDIT.value:
                    if file_count != 1:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": "Validation Error",
                                "message": f"Model '{model}' requires exactly 1 image file. You provided {file_count} files."
                            }
                        )
                # gemini_nanobanana and seedream allow 0-4 images
                elif file_count > max_allowed:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Validation Error",
                            "message": f"Model '{model}' supports up to {max_allowed} image files. You provided {file_count} files."
                        }
                    )

        # Generate/edit the image
        image_url = await image_generation_service.generate_image(
            prompt=prompt,
            model=model,
            mode=mode,
            user_id=user_id,
            style=style,
            shape=shape,
            image_files=image_files
        )

        success_message = f"Image {'generated' if mode == 'generate' else 'edited'} successfully using {model}"

        return ImageGenerationResponse(
            status=200,
            success_message=success_message,
            image_url=image_url,
            model_used=model,
            shape=shape
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        raise handle_service_error(e, model, "image generation")

@router.get("/models")
async def get_available_models():
    """Get list of available models for image generation"""
    return {
        "text_to_image_models": [
            {
                "name": model.value, 
                "description": f"{model.value.replace('_', ' ').title()} Model",
                "supports_edit": model in IMAGE_EDIT_MODELS
            } 
            for model in TEXT_TO_IMAGE_MODELS
        ],
        "image_edit_models": [
            {
                "name": model.value, 
                "description": f"{model.value.replace('_', ' ').title()} Model",
                "max_reference_images": MODEL_MAX_IMAGES.get(model, 0),
                "supports_generate": model in TEXT_TO_IMAGE_MODELS
            } 
            for model in IMAGE_EDIT_MODELS
        ]
    }
