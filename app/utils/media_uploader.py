import os
import io
import logging
import mimetypes
from datetime import datetime
from typing import Optional, Union
import requests
from PIL import Image
from ..core.config import config

logger = logging.getLogger(__name__)

class MediaUploader:
    """Centralized utility for uploading media files to cloud storage"""

    def __init__(self):
        self.storage_client = None
        self.bucket = None
        try:
            from google.cloud import storage
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(config.GCS_BUCKET_NAME)
            logger.info("GCS client initialized successfully")
        except ImportError:
            logger.warning("Google Cloud Storage not available, will fallback to local storage.")
        except Exception as e:
            logger.warning(f"Failed to initialize GCS client: {e}. Will fallback to local storage.")

    async def upload_image_from_url(
        self,
        image_url: str,
        prompt: str,
        user_id: str,
        style: str,
        shape: str,
        model_prefix: str = "image"
    ) -> str:
        """
        Download image from URL and upload to cloud storage

        Args:
            image_url: URL of the image to download
            prompt: Original prompt for filename
            user_id: User ID for organization
            style: Image style
            shape: Image shape
            model_prefix: Prefix for filename (e.g., 'dalle', 'flux')

        Returns:
            str: Public URL of the uploaded image
        """
        try:
            # Create safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"{model_prefix}_{timestamp}_{style}_{shape}_{safe_prompt}.png"

            # Download image bytes
            response = requests.get(image_url)
            response.raise_for_status()
            data = response.content

            return await self.upload_bytes(
                data=data,
                filename=filename,
                user_id=user_id,
                content_type='image/png',
                media_type='image'
            )

        except Exception as e:
            logger.error(f"Error uploading image from URL: {str(e)}")
            raise

    async def upload_bytes(
        self,
        data: bytes,
        filename: str,
        user_id: str,
        content_type: str,
        media_type: str = 'image'
    ) -> str:
        """
        Upload bytes directly to cloud storage

        Args:
            data: File bytes
            filename: Filename
            user_id: User ID
            content_type: MIME type
            media_type: 'image' or 'video'

        Returns:
            str: Public URL
        """
        try:
            # Try GCS upload first
            if self.bucket:
                destination_blob_name = f"{media_type}/{user_id}/{filename}"
                blob = self.bucket.blob(destination_blob_name)
                blob.upload_from_string(data, content_type=content_type)
                public_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                logger.info(f"{media_type.title()} uploaded to GCS: {public_url}")
                return public_url

            # Fallback to local storage
            user_folder = os.path.join(f"{media_type}s", user_id or "anonymous")
            os.makedirs(user_folder, exist_ok=True)
            file_path = os.path.join(user_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(data)

            public_url = f"{config.BASE_URL}/{media_type}s/{user_id or 'anonymous'}/{filename}"
            logger.info(f"{media_type.title()} saved locally: {file_path}")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading {media_type} bytes: {str(e)}")
            raise

    async def upload_video_from_url(
        self,
        video_url: str,
        prompt: str,
        user_id: str,
        shape: str,
        model_prefix: str = "video"
    ) -> str:
        """
        Download video from URL and upload to cloud storage

        Args:
            video_url: URL of the video to download
            prompt: Original prompt for filename
            user_id: User ID
            shape: Video shape
            model_prefix: Prefix for filename

        Returns:
            str: Public URL of the uploaded video
        """
        try:
            # Create safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"{model_prefix}_{timestamp}_{shape}_{safe_prompt}.mp4"

            # Download video bytes
            response = requests.get(video_url)
            response.raise_for_status()
            data = response.content

            return await self.upload_bytes(
                data=data,
                filename=filename,
                user_id=user_id,
                content_type='video/mp4',
                media_type='video'
            )

        except Exception as e:
            logger.error(f"Error uploading video from URL: {str(e)}")
            raise

    async def upload_audio_from_url(
        self,
        audio_url: str,
        prompt: str,
        user_id: str,
        model_prefix: str = "audio"
    ) -> str:
        """
        Download audio from URL and upload to cloud storage

        Args:
            audio_url: URL of the audio to download
            prompt: Original prompt for filename
            user_id: User ID
            model_prefix: Prefix for filename

        Returns:
            str: Public URL of the uploaded audio
        """
        try:
            # Create safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"{model_prefix}_{timestamp}_{safe_prompt}.mp3"

            # Download audio bytes
            response = requests.get(audio_url)
            response.raise_for_status()
            data = response.content

            return await self.upload_bytes(
                data=data,
                filename=filename,
                user_id=user_id,
                content_type='audio/mpeg',
                media_type='audio'
            )

        except Exception as e:
            logger.error(f"Error uploading audio from URL: {str(e)}")
            raise

    def resize_image_if_needed(self, image_content: bytes, max_dimension: int = 4000) -> bytes:
        """
        Resize image if it exceeds maximum dimensions

        Args:
            image_content: Image bytes
            max_dimension: Maximum width or height

        Returns:
            bytes: Resized image bytes (or original if no resize needed)
        """
        try:
            image = Image.open(io.BytesIO(image_content))
            original_width, original_height = image.size
            
            if original_width <= max_dimension and original_height <= max_dimension:
                return image_content
            
            if original_width > original_height:
                new_width = max_dimension
                new_height = int((original_height * max_dimension) / original_width)
            else:
                new_height = max_dimension
                new_width = int((original_width * max_dimension) / original_height)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            output_buffer = io.BytesIO()
            format_to_use = image.format if image.format else 'JPEG'
            resized_image.save(output_buffer, format=format_to_use, quality=95)
            return output_buffer.getvalue()
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return image_content

# Create singleton instance
media_uploader = MediaUploader()