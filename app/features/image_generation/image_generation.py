import logging
import os
import base64
import uuid
import io
from typing import List, Union, Optional
from fastapi import UploadFile
from openai import OpenAI
import fal_client
from google import genai
from google.genai import types

from app.core.config import config
from app.utils.media_uploader import media_uploader
from .image_generation_schema import ImageModel, MODEL_MAX_IMAGES

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Consolidated service for all image generation and editing - ALL models in one file"""

    def __init__(self):
        """Initialize all API clients and configuration"""
        # OpenAI for DALL-E
        self.openai_client = OpenAI(api_key=config.OPEN_AI_API_KEY)
        
        # FAL.ai for Flux and Qwen models
        if config.FAL_API_KEY:
            os.environ["FAL_KEY"] = config.FAL_API_KEY
            fal_client.api_key = config.FAL_API_KEY
        
        # Gemini for Gemini models
        if config.GEMINI_API_KEY:
            self.gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        # Media uploader for storage
        self.uploader = media_uploader
        
        # Temp folder for Gemini image saving
        self.images_folder = "generated_images"
        os.makedirs(self.images_folder, exist_ok=True)

    async def generate_image(
        self,
        prompt: str,
        model: str,
        mode: str,
        user_id: str,
        style: str = "Photo",
        shape: str = "square",
        image_files: Union[List[UploadFile], None] = None
    ) -> str:
        """
        Main entry point - Generate or edit image based on model and mode

        Args:
            prompt: Text prompt
            model: Model name (dalle, flux-1-spro, gemini, etc.)
            mode: 'generate' or 'edit'
            user_id: User ID
            style: Image style (Photo, Illustration, Comic, etc.)
            shape: Image shape (square, portrait, landscape)
            image_files: Reference images for edit mode

        Returns:
            Image URL (GCS or local)
        """
        try:
            if mode == "generate":
                return await self._generate_from_text(prompt, model, user_id, style, shape)
            elif mode == "edit":
                if not image_files:
                    raise ValueError("Image files required for edit mode")
                return await self._edit_image(prompt, model, user_id, style, shape, image_files)
            else:
                raise ValueError(f"Invalid mode: {mode}")
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            raise

    # ==================== TEXT-TO-IMAGE GENERATION ====================

    async def _generate_from_text(self, prompt: str, model: str, user_id: str, style: str, shape: str) -> str:
        """Generate image from text using any model"""
        logger.info(f"Generating image with {model}: {prompt[:50]}...")
        
        styled_prompt = f"{prompt}, in {style.lower()} style"
        model_name = model.lower()
        
        # DALL-E (OpenAI)
        if model == ImageModel.DALLE.value:
            size_mapping = {"square": "1024x1024", "portrait": "1024x1792", "landscape": "1792x1024"}
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=styled_prompt,
                n=1,
                size=size_mapping.get(shape, "1024x1024"),
                quality="standard"
            )
            return await self.uploader.upload_image_from_url(
                response.data[0].url, prompt, user_id, style, shape, "dalle"
            )
        
        # FAL.ai models (Flux 1 SRPO, Flux Kontext Dev, Qwen)
        elif model in [ImageModel.FLUX_1_SPRO.value, ImageModel.FLUX_KONTEXT_DEV.value, ImageModel.QWEN.value]:
            shape_mapping = {"square": "square_hd", "portrait": "portrait_4_3", "landscape": "landscape_4_3"}
            styled_prompt = f"{style} style: {prompt}"
            
            # Determine FAL endpoint and parameters
            if model == ImageModel.FLUX_1_SPRO.value:
                endpoint = "fal-ai/flux-1/srpo"
                prefix = "flux1_srpo"
                steps, guidance = 28, 3.5
            elif model == ImageModel.FLUX_KONTEXT_DEV.value:
                endpoint = "fal-ai/flux-pro/kontext/max/text-to-image"
                prefix = "flux_kontext"
                steps, guidance = 28, 3.5
            else:  # QWEN
                endpoint = "fal-ai/qwen-image"
                prefix = "qwen"
                steps, guidance = 30, 4.0
            
            handler = fal_client.submit(
                endpoint,
                arguments={
                    "prompt": styled_prompt,
                    "image_size": shape_mapping.get(shape, "square_hd"),
                    "num_inference_steps": steps,
                    "guidance_scale": guidance,
                    "num_images": 1,
                    "enable_safety_checker": True
                }
            )
            
            result = handler.get()
            if not result or "images" not in result or not result["images"]:
                raise Exception(f"No images generated by {model}")
            
            return await self.uploader.upload_image_from_url(
                result["images"][0]["url"], prompt, user_id, style, shape, prefix
            )
        
        # Gemini Imagen 4.0
        elif model == ImageModel.GEMINI.value:
            aspect_ratio_mapping = {"square": "1:1", "portrait": "9:16", "landscape": "16:9"}
            result = self.gemini_client.models.generate_images(
                model="models/imagen-4.0-generate-001",
                prompt=styled_prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio=aspect_ratio_mapping.get(shape, "1:1"),
                    image_size="1K"
                )
            )
            
            if not result.generated_images:
                raise Exception("No images generated by Gemini")
            
            filename = f"gemini_{style}_{shape}_{uuid.uuid4().hex}.jpg"
            
            # Save to buffer
            buf = io.BytesIO()
            try:
                result.generated_images[0].image.save(buf)
                buf.seek(0)
                image_bytes = buf.read()
            except TypeError:
                filepath = os.path.join(self.images_folder, filename)
                result.generated_images[0].image.save(filepath)
                with open(filepath, 'rb') as f:
                    image_bytes = f.read()
                try:
                    os.remove(filepath)
                except:
                    pass
            
            return await self.uploader.upload_bytes(
                image_bytes, filename, user_id, 'image/jpeg', 'image'
            )
        
        # Gemini NanoBanana (streaming)
        elif model == ImageModel.GEMINI_NANOBANANA.value:
            return await self._generate_gemini_streaming(prompt, user_id, style, shape, None)
        
        # SeeDream
        elif model == ImageModel.SEEDREAM.value:
            return await self._generate_seedream(prompt, user_id, style, shape, None)
        
        else:
            raise ValueError(f"Model {model} not supported for text-to-image generation")

    async def _generate_gemini_streaming(self, prompt: str, user_id: str, style: str, shape: str, 
                                          image_files: Optional[List[UploadFile]]) -> str:
        """Gemini NanoBanana streaming - supports text-to-image and image editing (0-4 images)"""
        styled_prompt = f"{prompt}, in {style.lower()} style"
        content_parts = [types.Part.from_text(text=styled_prompt)]
        
        # Add reference images if provided
        if image_files and len(image_files) > 0:
            max_images = min(len(image_files), 4)
            successfully_added = 0
            
            for i, image_file in enumerate(image_files[:max_images]):
                if image_file and image_file.filename:
                    try:
                        image_content = await image_file.read()
                        resized_content = self.uploader.resize_image_if_needed(image_content)
                        content_parts.append(
                            types.Part.from_bytes(
                                data=resized_content,
                                mime_type=image_file.content_type or "image/jpeg"
                            )
                        )
                        successfully_added += 1
                    except Exception as e:
                        logger.warning(f"Failed to process reference image: {e}")
            
            if successfully_added > 0:
                styled_prompt = f"{styled_prompt}. Use the provided {successfully_added} reference image{'s' if successfully_added > 1 else ''} as visual reference."
                content_parts[0] = types.Part.from_text(text=styled_prompt)
        
        contents = [types.Content(role="user", parts=content_parts)]
        generate_content_config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        
        file_index = 0
        for chunk in self.gemini_client.models.generate_content_stream(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
            config=generate_content_config
        ):
            if (chunk.candidates and chunk.candidates[0].content and 
                chunk.candidates[0].content.parts and
                chunk.candidates[0].content.parts[0].inline_data and
                chunk.candidates[0].content.parts[0].inline_data.data):
                
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                mime_type = inline_data.mime_type
                import mimetypes
                file_extension = mimetypes.guess_extension(mime_type) or ".png"
                
                filename = f"nanobanana_{style}_{shape}_{uuid.uuid4().hex}_{file_index}{file_extension}"
                return await self.uploader.upload_bytes(data_buffer, filename, user_id, mime_type, 'image')
        
        raise Exception("No image data received from Gemini NanoBanana")

    async def _generate_seedream(self, prompt: str, user_id: str, style: str, shape: str, 
                                  image_files: Optional[List[UploadFile]]) -> str:
        """SeeDream - supports text-to-image and image editing (0-4 images)"""
        styled_prompt = f"{style} style: {prompt}"
        shape_mapping = {"square": "square", "portrait": "portrait", "landscape": "landscape"}
        image_size = shape_mapping.get(shape, "square")
        
        arguments = {
            "prompt": styled_prompt,
            "aspect_ratio": image_size,
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "num_images": 1
        }
        
        # Add image references if editing
        if image_files and len(image_files) > 0:
            if len(image_files) > 4:
                raise ValueError("Maximum 4 images allowed")
            
            image_data_urls = []
            for image_file in image_files:
                image_content = await image_file.read()
                resized_content = self.uploader.resize_image_if_needed(image_content)
                image_base64 = base64.b64encode(resized_content).decode('utf-8')
                image_data_url = f"data:{image_file.content_type};base64,{image_base64}"
                image_data_urls.append(image_data_url)
            
            arguments["image_urls"] = image_data_urls
            endpoint = "fal-ai/bytedance/seedream/v4/edit"
        else:
            endpoint = "fal-ai/bytedance/seedream/v4/text-to-image"
        
        handler = fal_client.submit(endpoint, arguments=arguments)
        result = handler.get()
        
        if not result or "images" not in result or not result["images"]:
            raise Exception("No images generated by SeeDream")
        
        image_url = result["images"][0]["url"]
        num_imgs = len(image_files) if image_files else 0
        prefix = f"seedream_{'edit' if num_imgs > 0 else 'gen'}"
        return await self.uploader.upload_image_from_url(image_url, prompt, user_id, style, shape, prefix)

    # ==================== IMAGE EDITING ====================

    async def _edit_image(self, prompt: str, model: str, user_id: str, style: str, shape: str, 
                          image_files: List[UploadFile]) -> str:
        """Edit image using any model"""
        # Validate file count
        max_files = MODEL_MAX_IMAGES.get(model, 0)
        if len(image_files) > max_files:
            raise ValueError(f"Model {model} supports maximum {max_files} reference images")

        logger.info(f"Editing image with {model}: {prompt[:50]}...")
        
        # Flux Kontext Edit (1 image required)
        if model == ImageModel.FLUX_KONTEXT_EDIT.value:
            image_content = await image_files[0].read()
            resized_content = self.uploader.resize_image_if_needed(image_content)
            image_base64 = base64.b64encode(resized_content).decode('utf-8')
            image_data_url = f"data:{image_files[0].content_type};base64,{image_base64}"
            
            styled_prompt = f"{style} style: {prompt}"
            shape_mapping = {"square": "square_hd", "portrait": "portrait_4_3", "landscape": "landscape_4_3"}
            
            handler = fal_client.submit(
                "fal-ai/flux-pro/kontext/max",
                arguments={
                    "prompt": styled_prompt,
                    "image_url": image_data_url,
                    "image_size": shape_mapping.get(shape, "square_hd"),
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "num_images": 1,
                    "enable_safety_checker": True
                }
            )
            
            result = handler.get()
            if not result or "images" not in result or not result["images"]:
                raise Exception("No images generated by Flux Kontext Edit")
            
            return await self.uploader.upload_image_from_url(
                result["images"][0]["url"], prompt, user_id, style, shape, "flux_edit"
            )
        
        # Gemini NanoBanana (0-4 images)
        elif model == ImageModel.GEMINI_NANOBANANA.value:
            return await self._generate_gemini_streaming(prompt, user_id, style, shape, image_files)
        
        # SeeDream (0-4 images)
        elif model == ImageModel.SEEDREAM.value:
            return await self._generate_seedream(prompt, user_id, style, shape, image_files)
        
        else:
            raise ValueError(f"Model {model} not supported for image editing")




# Create singleton instance
image_generation_service = ImageGenerationService()
