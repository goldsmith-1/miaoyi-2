"""Loads markdown files into pgvector. Usage: python -m scripts.ingest data/knowledge

File format: first line '# Title', optional 'source: ...' line, then the body text."""
import asyncio
import sys
from pathlib import Path

import psycopg

from app import rag
from app.config import settings
from app.db import to_vector


def chunk(text: str, size: int = 800) -> list[str]:
    out, cur = [], ""
    for para in (p.strip() for p in text.split("\n\n") if p.strip()):
        if cur and len(cur) + len(para) > size:
            out.append(cur)
            cur = ""
        cur = f"{cur}\n\n{para}".strip()
    return out + [cur] if cur else out


async def main(folder: str) -> None:
    rows = []
    for path in sorted(Path(folder).glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        title = lines[0].lstrip("# ").strip() if lines else path.stem
        source = next((l.split(":", 1)[1].strip() for l in lines[1:3] if l.lower().startswith("source:")), path.name)
        body = "\n".join(l for l in lines[1:] if not l.lower().startswith("source:"))
        for piece in chunk(body):
            rows.append((title, source, piece, to_vector(await rag.embed(piece))))
    with psycopg.connect(settings.database_url) as conn:
        conn.cursor().executemany(
            "INSERT INTO knowledge_chunks (title, source, content, embedding) VALUES (%s, %s, %s, %s::vector)", rows
        )
    print(f"Inserted {len(rows)} chunks")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "data/knowledge"))
