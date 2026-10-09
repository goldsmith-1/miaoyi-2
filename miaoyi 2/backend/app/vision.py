import base64

import httpx
from fastapi import HTTPException

from .config import settings


async def extract_text(image: bytes) -> str:
    """OCR a photo (for example a medicine or ingredient label) with Google Cloud Vision."""
    if not settings.google_vision_api_key:
        raise HTTPException(503, "Image reading is not configured")
    body = {"requests": [{"image": {"content": base64.b64encode(image).decode()}, "features": [{"type": "TEXT_DETECTION"}]}]}
    async with httpx.AsyncClient(timeout=30) as http:
        resp = await http.post(
            "https://vision.googleapis.com/v1/images:annotate",
            headers={"X-Goog-Api-Key": settings.google_vision_api_key},
            json=body,
        )
    if resp.status_code != 200:
        raise HTTPException(502, "The image service failed. Try again.")
    annotation = resp.json()["responses"][0].get("fullTextAnnotation")
    return annotation["text"].strip() if annotation else ""
