"""
AI Query Master - Schema Builder API
POST /api/build-schema
Accepts an image upload and uses vision models to generate SQL DDL.
Fallback chain: Gemini 2.0 Flash → Groq Llama 4 Scout → OpenRouter Vision
"""
import os
import io
import base64
import time
import logging
import httpx
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Schema Builder"])


def _build_prompt(db_type: str) -> str:
    return f"""Analyze this database schema diagram image and generate valid {db_type.upper()} DDL (CREATE TABLE statements).

Requirements:
- Generate syntactically correct {db_type.upper()} CREATE TABLE statements
- Include proper data types for {db_type}
- Add PRIMARY KEY constraints
- Add FOREIGN KEY constraints where relationships are visible
- Add NOT NULL constraints where appropriate
- Add indexes for foreign keys
- Use proper naming conventions (snake_case)

Return ONLY the SQL DDL statements, no explanations. After the SQL, add a section starting with "---NOTES---" with brief notes about any assumptions made."""


def _parse_response(text: str) -> dict:
    """Split response into schema and notes."""
    if "---NOTES---" in text:
        parts = text.split("---NOTES---")
        schema = parts[0].strip()
        notes = parts[1].strip()
    else:
        schema = text.strip()
        notes = ""
    # Clean markdown code fences
    for fence in ["```sql", "```mysql", "```postgresql", "```"]:
        schema = schema.replace(fence, "")
    schema = schema.strip()
    return {"schema": schema, "analysis": notes}


async def generate_with_gemini_vision(image_bytes: bytes, db_type: str) -> dict:
    """Use Gemini Vision to analyze schema diagram."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("Gemini API key not configured")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    image_part = {"mime_type": "image/png", "data": image_bytes}
    response = model.generate_content([_build_prompt(db_type), image_part])

    result = _parse_response(response.text)
    result["provider"] = "Gemini 2.0 Flash"
    return result


async def generate_with_groq_vision(image_bytes: bytes, db_type: str) -> dict:
    """Use Groq with Llama 4 Scout (vision-capable)."""
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("Groq API key not configured")

    client = Groq(api_key=api_key)
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _build_prompt(db_type)},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                    },
                ],
            }
        ],
        max_tokens=4096,
    )

    result = _parse_response(response.choices[0].message.content)
    result["provider"] = "Groq Llama 4 Scout"
    return result


async def generate_with_openrouter_vision(image_bytes: bytes, db_type: str) -> dict:
    """Use OpenRouter with a free vision model."""
    api_key = os.getenv("OPENROUTER_KEY_1")
    if not api_key:
        raise Exception("OpenRouter API key not configured")

    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-4-scout:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": _build_prompt(db_type)},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                            },
                        ],
                    }
                ],
                "max_tokens": 4096,
            },
        )
        response.raise_for_status()
        data = response.json()

    text = data["choices"][0]["message"]["content"]
    result = _parse_response(text)
    result["provider"] = "OpenRouter Llama 4 Scout"
    return result


@router.post("/build-schema")
async def build_schema(
    image: UploadFile = File(...),
    db_type: str = Form(default="mysql"),
):
    """Generate SQL DDL from a schema diagram image."""
    if db_type not in ("mysql", "postgresql"):
        raise HTTPException(400, "db_type must be 'mysql' or 'postgresql'")

    allowed = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    if image.content_type not in allowed:
        raise HTTPException(400, "Only PNG, JPG, WebP images are accepted")

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image must be under 10MB")

    start_time = time.time()

    providers = [
        ("Gemini Vision", generate_with_gemini_vision),
        ("Groq Vision", generate_with_groq_vision),
        ("OpenRouter Vision", generate_with_openrouter_vision),
    ]

    last_error = None
    for name, func in providers:
        try:
            logger.info(f"Trying {name}...")
            result = await func(image_bytes, db_type)
            elapsed = round(time.time() - start_time, 2)
            result["time_seconds"] = elapsed
            logger.info(f"✓ {name} succeeded in {elapsed}s")
            return result
        except Exception as e:
            logger.warning(f"✗ {name} failed: {e}")
            last_error = e

    raise HTTPException(500, f"All vision providers failed: {str(last_error)}")
