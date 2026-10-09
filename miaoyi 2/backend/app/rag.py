"""Retrieval-augmented answers: embed the question, fetch similar chunks from pgvector, answer with GPT-4o using only that context."""
from openai import AsyncOpenAI

from . import db
from .config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key or "unset")
MIN_SCORE = 0.30
MAX_HISTORY = 6

SYSTEM_PROMPT = """You are Miaoyi, a health information assistant that explains Traditional Chinese Medicine and modern medicine side by side.
Rules:
- Answer only from the numbered context below. If it does not cover the question, say you do not have reliable information.
- Cite sources like [1] after the claims they support.
- You provide general information, not diagnosis or treatment. Never tell the user to start, stop or change a medicine.
- Mention when TCM and modern medicine disagree or when evidence is limited.
- Encourage seeing a doctor or pharmacist for symptoms that are severe, persistent or worrying.
- Reply in the same language as the user's question."""

EMERGENCY_TERMS = [
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing", "overdose",
    "suicid", "severe bleeding", "stroke", "胸痛", "呼吸困难", "自杀", "大出血", "中风",
]
EMERGENCY_NOTICE = (
    "If this is an emergency or you may be in danger, contact your local emergency number or go to the nearest "
    "hospital now. This app cannot provide emergency care."
)
NO_ANSWER = "I don't have reliable information on that yet. Please ask a doctor or pharmacist."


def needs_emergency_notice(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in EMERGENCY_TERMS)


def build_messages(question: str, chunks: list[dict], history: list[dict]) -> list[dict]:
    context = "\n\n".join(f"[{i}] {c['title']} ({c['source']})\n{c['content']}" for i, c in enumerate(chunks, 1))
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context}"}]
    messages += [{"role": h["role"], "content": h["content"]} for h in history[-MAX_HISTORY:]]
    messages.append({"role": "user", "content": question})
    return messages


async def embed(text: str) -> list[float]:
    resp = await client.embeddings.create(model=settings.embedding_model, input=text)
    return resp.data[0].embedding


async def answer(question: str, history: list[dict]) -> dict:
    chunks = [c for c in await db.search(await embed(question), 5) if c["score"] >= MIN_SCORE]
    notice = EMERGENCY_NOTICE + "\n\n" if needs_emergency_notice(question) else ""
    if not chunks:
        return {"answer": notice + NO_ANSWER, "sources": []}
    resp = await client.chat.completions.create(
        model=settings.chat_model, messages=build_messages(question, chunks, history), temperature=0.2
    )
    sources = [{"n": i, "title": c["title"], "source": c["source"]} for i, c in enumerate(chunks, 1)]
    return {"answer": notice + (resp.choices[0].message.content or ""), "sources": sources}
