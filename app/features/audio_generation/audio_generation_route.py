from fastapi import APIRouter, HTTPException, Header
import logging
from .audio_generation import audio_generation_service
from .audio_generation_schema import AudioGenerationRequest, AudioGenerationResponse
from ...core.error_handlers import handle_service_error

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=AudioGenerationResponse)
async def generate_audio(
    request: AudioGenerationRequest,
    user_id: str = Header(None)
):
    """
    Generate audio/music using AI model
    
    **Available Model:**
    - `minimax` - MiniMax Music v1.5 (verse prompt required, lyrics_prompt optional for style)
    
    **Request Body:**
    ```json
    {
        "verse_prompt": "Description of the music (required)",
        "lyrics_prompt": "Optional lyrics/style description"
    }
    ```
    """
    try:
        # Validate verse_prompt
        if not request.verse_prompt or not request.verse_prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation Error", "message": "Verse prompt is required"}
            )

        # Generate the audio
        audio_url = await audio_generation_service.generate_audio(
            verse_prompt=request.verse_prompt,
            user_id=user_id,
            lyrics_prompt=request.lyrics_prompt
        )

        success_message = "Audio generated successfully using MiniMax"

        return AudioGenerationResponse(
            status=200,
            success_message=success_message,
            audio_url=audio_url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in audio generation: {str(e)}")
        raise handle_service_error(e, "minimax", "audio generation")
