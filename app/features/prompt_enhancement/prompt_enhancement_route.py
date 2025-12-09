from fastapi import APIRouter, HTTPException
import logging
from .prompt_enhancement import prompt_enhancement_service
from .prompt_enhancement_schema import PromptEnhancementRequest, PromptEnhancementResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/enhance", response_model=PromptEnhancementResponse)
async def enhance_prompt(request: PromptEnhancementRequest):
    """
    Enhance a prompt for better AI generation results
    
    **Uses OpenAI GPT-4o to improve prompts**
    
    **Supported Types:**
    - `image` - Enhances for image generation (adds visual details, style, composition)
    - `video` - Enhances for video generation (adds motion, cinematography, transitions)
    - `audio` - Enhances for audio/music generation (adds mood, instruments, tempo)
    
    **Request Body:**
    ```json
    {
        "prompt": "Your original prompt text",
        "type": "image"
    }
    ```
    
    **Response:**
    - Returns enhanced prompt optimized for the specified media type
    """
    try:
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": "Prompt is required"}
            )

        if request.type not in ["image", "video", "audio"]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": "Type must be image, video, or audio"}
            )

        enhanced_prompt = await prompt_enhancement_service.enhance_prompt(
            prompt=request.prompt,
            type=request.type
        )

        return PromptEnhancementResponse(
            status=200,
            success_message="Prompt enhanced successfully",
            enhanced_prompt=enhanced_prompt
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in prompt enhancement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance prompt: {str(e)}"
        )
