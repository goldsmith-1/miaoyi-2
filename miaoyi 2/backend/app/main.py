from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from . import db
from .config import settings
from .routers import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = aioredis.from_url(settings.redis_url)
    await db.open_pool()
    yield
    await db.close_pool()
    await app.state.redis.aclose()


app = FastAPI(title="Miaoyi API", version="1.0.0", lifespan=lifespan)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
