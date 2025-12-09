import logging
import openai
from app.core.config import config

logger = logging.getLogger(__name__)


class PromptEnhancementService:
    """Consolidated service for prompt enhancement - supports image, video, and audio"""

    def __init__(self):
        """Initialize OpenAI client for prompt enhancement"""
        if not config.OPEN_AI_API_KEY:
            raise ValueError("OPEN_AI_API_KEY is required for prompt enhancement")
        
        self.client = openai.OpenAI(api_key=config.OPEN_AI_API_KEY)

    async def enhance_prompt(self, prompt: str, type: str = "image") -> str:
        """
        Enhance a prompt for better AI generation using GPT-4

        Args:
            prompt: Original prompt to enhance
            type: Content type - 'image', 'video', or 'audio'

        Returns:
            Enhanced prompt string
        """
        try:
            logger.info(f"Enhancing {type} prompt: {prompt[:50]}...")
            
            if type.lower() == "image":
                system_prompt = self._get_image_system_prompt()
                user_message = f"""Enhance this prompt for AI image generation: "{prompt}"
                
                Return only the enhanced prompt, no explanations."""
            
            elif type.lower() == "video":
                system_prompt = self._get_video_system_prompt()
                user_message = f"""Enhance this prompt for AI video generation: "{prompt}"
                
                Return only the enhanced prompt, no explanations."""
            
            elif type.lower() == "audio":
                system_prompt = self._get_audio_system_prompt()
                user_message = f"""Enhance this prompt for AI audio/music generation: "{prompt}"
                
                Return only the enhanced prompt, no explanations."""
            
            else:
                raise ValueError(f"Invalid type: {type}. Must be 'image', 'video', or 'audio'")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            
            logger.info(f"{type.capitalize()} prompt enhanced successfully")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            raise Exception(f"Failed to enhance prompt: {str(e)}")


    def _get_image_system_prompt(self) -> str:
        """System prompt for image generation enhancement"""
        return """You are an expert at enhancing prompts for AI image generation. 
        Take the user's prompt and improve it by adding artistic details, quality terms, and technical specifications 
        that will help generate better images. Keep the original concept but make it more detailed and specific.
        
        Focus on: visual style, lighting, composition, colors, mood, artistic medium, quality descriptors."""

    def _get_video_system_prompt(self) -> str:
        """System prompt for video generation enhancement"""
        return """You are an expert at enhancing prompts for AI video generation. 
        Take the user's prompt and improve it by adding details about motion, cinematography, pacing, and visual flow 
        that will help generate better videos. Keep the original concept but make it more detailed and specific.
        
        Focus on: camera movements, scene transitions, motion dynamics, temporal flow, lighting changes, cinematographic style."""

    def _get_audio_system_prompt(self) -> str:
        """System prompt for audio/music generation enhancement"""
        return """You are an expert at enhancing prompts for AI music/audio generation. 
        Take the user's prompt and improve it by adding artistic details, quality terms, and technical specifications 
        that will help generate better music/audio. Keep the original concept but make it more detailed and specific.
        
        Focus on: musical style, instruments, tempo, mood, harmony, rhythm, production quality."""

prompt_enhancement_service = PromptEnhancementService()
