import logging
import os
import requests
from datetime import datetime
import fal_client
import io
from fastapi import UploadFile
from app.core.config import config
from app.utils.media_uploader import media_uploader
from PIL import Image

logger = logging.getLogger(__name__)

class AIAvatarService:
    """Service for generating videos using ByteDance OmniHuman from FAL.ai"""
    
    def __init__(self):
        self.api_key = config.FAL_API_KEY
        if not self.api_key:
            raise ValueError("FAL_API_KEY is required in .env file")
        
        # Configure FAL client
        os.environ["FAL_KEY"] = self.api_key
        fal_client.api_key = self.api_key
        
        # Media uploader for storage
        self.uploader = media_uploader

    async def generate_video(self, image_file: UploadFile, audio_file: UploadFile,user_id: str) -> str:
        """
        Generate a video using ByteDance OmniHuman and save it locally
        
        Args:
            image_file (UploadFile): The input image file
            audio_file (UploadFile): The input audio file
            
        Returns:
            str: Local video URL
        """
        try:
            logger.info(f"Generating AI Avatar video with image {image_file.filename} and audio {audio_file.filename}...")
            

            # Read file contents
            image_content = await image_file.read()
            audio_content = await audio_file.read()

            # Resize image if needed (min 512x512, max 4000x4000 for FAL.ai)
            try:
                image_stream = io.BytesIO(image_content)
                with Image.open(image_stream) as img:
                    width, height = img.size
                    logger.info(f"Original image dimensions: {width}x{height}")
                    
                    needs_resize = False
                    new_width, new_height = width, height
                    
                    # Check if image exceeds FAL.ai maximum dimensions (4000x4000)
                    if width > 4000 or height > 4000:
                        logger.info(f"Image exceeds FAL.ai maximum dimensions, resizing from {width}x{height}...")
                        # Scale down while maintaining aspect ratio
                        if width > height:
                            new_width = 4000
                            new_height = int((height * 4000) / width)
                        else:
                            new_height = 4000
                            new_width = int((width * 4000) / height)
                        needs_resize = True
                    
                    # Check if image is below minimum dimensions (512x512)
                    if new_width < 512 or new_height < 512:
                        logger.info(f"Image below minimum dimensions, resizing to at least 512x512...")
                        new_width = max(new_width, 512)
                        new_height = max(new_height, 512)
                        needs_resize = True
                    
                    if needs_resize:
                        logger.info(f"Resizing image to: {new_width}x{new_height}")
                        # Resize the image
                        img = img.convert("RGB")
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Save resized image
                        out_stream = io.BytesIO()
                        resized_img.save(out_stream, format="JPEG", quality=95)
                        image_content = out_stream.getvalue()
                        logger.info(f"Image resized successfully to {new_width}x{new_height}")
                    else:
                        logger.info("Image dimensions are within acceptable limits, no resizing needed")
                        
            except Exception as e:
                logger.warning(f"Could not resize image: {e}. Proceeding with original image.")

            # Reset file pointers for potential re-reading
            await image_file.seek(0)
            await audio_file.seek(0)

            # Upload files to FAL.ai storage
            logger.info("Uploading image file to FAL.ai storage...")
            image_url = fal_client.upload(
                image_content,
                content_type="image/jpeg"
            )

            logger.info("Uploading audio file to FAL.ai storage...")
            audio_url = fal_client.upload(
                audio_content,
                content_type=audio_file.content_type
            )

            logger.info(f"Using uploaded image URL: {image_url}")
            logger.info(f"Using uploaded audio URL: {audio_url}")
            
            # Submit the request to FAL.ai
            handler = fal_client.submit(
                "fal-ai/bytedance/omnihuman",
                arguments={
                    "image_url": image_url,
                    "audio_url": audio_url
                }
            )
            
            # Get the result
            result = handler.get()
            
            if not result or "video" not in result or not result["video"]:
                raise Exception("No video generated by FAL.ai")
            
            # Get the video URL
            video_url = result["video"]["url"]
            
            # Upload video to storage using media_uploader
            safe_name = "".join(c for c in image_file.filename[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            uploaded_url = await self.uploader.upload_video_from_url(
                video_url, 
                safe_name, 
                user_id, 
                "landscape",
                "ai_avatar"
            )
            
            logger.info(f"Successfully generated AI Avatar video: {uploaded_url}")
            return uploaded_url
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise


# Create a singleton instance
ai_avatar_service = AIAvatarService()
