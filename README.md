# 🎨 Dream Canvas Art - AI Media Generation Platform

> **Transform your imagination into reality with cutting-edge AI models** 🚀

A powerful, production-ready FastAPI service that brings together the best AI models for **image generation**, **video creation**, **audio/music production**, and **intelligent prompt enhancement**. Built with efficiency, scalability, and ease of use in mind.

---

## ✨ Features

### 🖼️ **Image Generation**
Generate stunning images or edit existing ones using 8 different AI models:

- **DALL-E 3** - OpenAI's flagship text-to-image model
- **Flux 1 SPRO** - High-quality artistic generation
- **Flux Kontext Dev** - Context-aware image creation
- **Flux Kontext Edit** - Advanced image editing (1 reference image)
- **Gemini Imagen 4.0** - Google's latest image model
- **Gemini NanoBanana** - Streaming generation with up to 4 reference images
- **Qwen Image** - Fast and efficient generation
- **SeeDream** - Creative editing with up to 4 reference images

**Modes:**
- 🎯 **Text-to-Image** - Generate from descriptions
- ✏️ **Image Editing** - Transform existing images (0-4 reference images depending on model)

**Styles:** Photo, Illustration, Comic, Anime, Realistic, Abstract, Fantasy, Cyberpunk, Vintage, Minimalist

**Aspect Ratios:** Square (1:1), Portrait (9:16), Landscape (16:9)

---

### 🎬 **Video Generation**
Create dynamic videos from text or images using 4 powerful models:

- **Veo 2.0** - Google's advanced video generation
- **Veo 3.0 Fast** - Rapid video creation
- **Pixverse Text-to-Video** - Narrative video generation
- **Pixverse Image-to-Video** - Animate your images

**Modes:**
- 📝 **Text-to-Video** - Generate from descriptions
- 🖼️ **Image-to-Video** - Bring images to life

**Aspect Ratios:** Portrait (9:16), Landscape (16:9)

---

### 🎵 **Audio Generation**
Produce professional music tracks with AI:

- **MiniMax Music v1.5** - High-quality music generation with automatic prompt enhancement
- **GPT-4o Enhancement** - Intelligent verse and style optimization (under 300 characters)

**Features:**
- Automatic verse/lyrics enhancement
- Optional music style enhancement
- Professional-quality output

---

### 🧠 **Prompt Enhancement**
Optimize your prompts for better results:

- **GPT-4o Powered** - Context-aware enhancement
- **Type-Specific** - Tailored for image, video, or audio generation
- **Intelligent Optimization** - Improves clarity and detail

---

## 🏗️ Architecture

### Project Structure
```
Dream Canvas Art/
├── app/
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   └── error_handlers.py      # Global error handling
│   ├── features/
│   │   ├── image_generation/      # 🖼️ Image generation (3 files)
│   │   │   ├── image_generation.py
│   │   │   ├── image_generation_route.py
│   │   │   └── image_generation_schema.py
│   │   ├── video_generation/      # 🎬 Video generation (3 files)
│   │   │   ├── video_generation.py
│   │   │   ├── video_generation_route.py
│   │   │   └── video_generation_schema.py
│   │   ├── audio_generation/      # 🎵 Audio generation (3 files)
│   │   │   ├── audio_generation.py
│   │   │   ├── audio_generation_route.py
│   │   │   └── audio_generation_schema.py
│   │   └── prompt_enhancement/    # 🧠 Prompt enhancement (3 files)
│   │       ├── prompt_enhancement.py
│   │       ├── prompt_enhancement_route.py
│   │       └── prompt_enhancement_schema.py
│   └── utils/
│       ├── content_policy_checker.py  # Content safety
│       ├── delete_user_info.py        # Data management
│       └── media_uploader.py          # 📦 Centralized upload utility
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Multi-service orchestration
├── .env.example                   # Environment template
└── README.md                      # This file
```

### 🎯 Design Principles

- **✅ Single Responsibility** - Each feature has exactly 3 files (service, route, schema)
- **✅ DRY (Don't Repeat Yourself)** - Consolidated logic in generic functions
- **✅ Centralized Utilities** - Shared functionality in `media_uploader.py`
- **✅ No External Imports** - All model logic self-contained in main service files
- **✅ Efficient Code** - Generic functions with conditional branching instead of model-specific functions

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- API Keys:
  - OpenAI API Key
  - FAL.ai API Key
  - Google Gemini API Key
  - Google Cloud Storage credentials (optional)

---

### 📦 Installation

#### **Option 1: Local Setup**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Dream Canvas Art"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

#### **Option 2: Docker Setup** 🐳

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the API**
   - API Documentation: http://localhost:8080/docs
   - ReDoc: http://localhost:8080/redoc

---

## 🔑 Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Keys (Required)
OPEN_AI_API_KEY=your_openai_api_key_here
FAL_API_KEY=your_fal_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Storage (Optional - falls back to local storage)
GCS_BUCKET_NAME=your_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Application Settings
BASE_URL=http://localhost:8080
PORT=8080
```

---

## 📡 API Endpoints

### 🖼️ Image Generation
```http
POST /api/image/generate
Content-Type: multipart/form-data

Parameters:
- prompt (string): Text description
- model (string): dalle, flux-1-spro, gemini, flux-kontext-dev, qwen, 
                  gemini-nanobanana, flux-kontext-edit, seedream
- mode (string): generate or edit
- user_id (string): User identifier
- style (string): Photo, Illustration, Comic, etc.
- shape (string): square, portrait, landscape
- image_files (files, optional): Reference images for edit mode
```

### 🎬 Video Generation
```http
POST /api/video/generate
Content-Type: multipart/form-data

Parameters:
- prompt (string): Text description
- model (string): veo-2, veo-3-fast, pixverse
- mode (string): generate (text-to-video) or edit (image-to-video)
- user_id (string): User identifier
- shape (string): portrait, landscape
- image_file (file, optional): Reference image for image-to-video
```

### 🎵 Audio Generation
```http
POST /api/audio/generate
Content-Type: application/json

Body:
{
  "verse_prompt": "Your lyrics/verse text",
  "user_id": "user123",
  "lyrics_prompt": "Optional music style description"
}
```

### 🧠 Prompt Enhancement
```http
POST /api/prompt/enhance
Content-Type: application/json

Body:
{
  "prompt": "Your original prompt",
  "type": "image" | "video" | "audio"
}
```

### 🗑️ Delete User Data
```http
DELETE /api/delete-user-data/{user_id}
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Framework** | FastAPI, Uvicorn |
| **AI/ML** | OpenAI (GPT-4o, DALL-E 3), Google Gemini (Imagen, Veo), FAL.ai (Flux, Pixverse, MiniMax) |
| **Image Processing** | Pillow (PIL) |
| **Storage** | Google Cloud Storage (with local fallback) |
| **Validation** | Pydantic |
| **Containerization** | Docker, Docker Compose |

---

## 📊 Model Comparison

### Image Models

| Model | Speed | Quality | Editing | Reference Images |
|-------|-------|---------|---------|------------------|
| DALL-E 3 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | 0 |
| Flux 1 SPRO | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | 0 |
| Flux Kontext Dev | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | 0 |
| Flux Kontext Edit | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 1 (required) |
| Gemini Imagen | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | 0 |
| Gemini NanoBanana | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 0-4 |
| Qwen | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | 0 |
| SeeDream | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 0-4 |

### Video Models

| Model | Speed | Quality | Mode |
|-------|-------|---------|------|
| Veo 2.0 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Text-to-Video |
| Veo 3.0 Fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Text-to-Video |
| Pixverse (Text) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Text-to-Video |
| Pixverse (Image) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Image-to-Video |

---

## 🎯 Use Cases

- 🎨 **Digital Art Creation** - Generate unique artwork for projects
- 📱 **Social Media Content** - Create engaging visuals and videos
- 🎬 **Video Production** - Quick video prototyping and storyboarding
- 🎵 **Music Production** - Generate background music and soundtracks
- 🖼️ **Image Editing** - Transform and enhance existing images
- 📝 **Content Marketing** - Automated visual content generation

---

## 🔒 Security Features

- ✅ Content policy checking
- ✅ User data management and deletion
- ✅ Secure API key handling via environment variables
- ✅ Input validation and sanitization
- ✅ Error handling without exposing sensitive information
- ✅ CORS configuration for web applications

---

## 🚦 Error Handling

The API provides comprehensive error responses:

```json
{
  "error": "Validation Error",
  "detail": "Detailed error message",
  "status_code": 422
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request
- `422` - Validation Error
- `500` - Internal Server Error

---

## 📈 Performance Optimization

- 🔥 **Consolidated Functions** - Reduced code duplication by ~160 lines
- 🔥 **Centralized Uploads** - Single utility for all media operations
- 🔥 **Efficient Routing** - Generic functions with conditional branching
- 🔥 **Image Optimization** - Automatic resizing (max 4000x4000)
- 🔥 **Async Operations** - Non-blocking I/O for better performance

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- OpenAI for DALL-E 3 and GPT-4o
- Google for Gemini AI (Imagen, Veo, NanoBanana)
- FAL.ai for Flux, Pixverse, Qwen, SeeDream, and MiniMax models
- FastAPI community for the excellent framework

---

## 📞 Support

- 📧 Email: support@xobehstudio.com
- 📚 Documentation: http://localhost:8080/docs
- 🐛 Issues: GitHub Issues

---

## 🎉 Quick Start Example

```python
import requests

# Generate an image
response = requests.post(
    "http://localhost:8080/api/image/generate",
    data={
        "prompt": "A futuristic city at sunset",
        "model": "dalle",
        "mode": "generate",
        "user_id": "user123",
        "style": "Cyberpunk",
        "shape": "landscape"
    }
)

image_url = response.json()["image_url"]
print(f"Generated image: {image_url}")
```

---


