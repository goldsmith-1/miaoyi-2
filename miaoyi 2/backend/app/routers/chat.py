import asyncio
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .. import rag, storage, vision
from ..ratelimit import rate_limit

router = APIRouter(prefix="/v1", tags=["chat"])
ALLOWED_IMAGES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[Turn] = []


@router.post("/chat")
async def chat(req: ChatRequest, user: dict = Depends(rate_limit)):
    return await rag.answer(req.message, [t.model_dump() for t in req.history])


@router.post("/scan")
async def scan(image: UploadFile = File(...), user: dict = Depends(rate_limit)):
    if image.content_type not in ALLOWED_IMAGES:
        raise HTTPException(415, "Upload a JPEG, PNG or WebP image")
    data = await image.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image is larger than 5 MB")
    text = await vision.extract_text(data)
    if not text:
        raise HTTPException(422, "No readable text found in the image")
    if storage.configured():
        await asyncio.to_thread(storage.upload_image, data, image.content_type, user["sub"])
    question = f"Explain this text from a product label in plain language, and note what to check with a pharmacist or doctor:\n{text[:1500]}"
    result = await rag.answer(question, [])
    return {"extracted_text": text, **result}
