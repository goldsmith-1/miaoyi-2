from psycopg_pool import AsyncConnectionPool

from .config import settings

pool: AsyncConnectionPool | None = None

SEARCH_SQL = """
SELECT title, source, content, 1 - (embedding <=> %s::vector) AS score
FROM knowledge_chunks
ORDER BY embedding <=> %s::vector
LIMIT %s
"""


async def open_pool() -> None:
    global pool
    pool = AsyncConnectionPool(settings.database_url, open=False)
    await pool.open()


async def close_pool() -> None:
    if pool:
        await pool.close()


def to_vector(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"


async def search(embedding: list[float], k: int = 5) -> list[dict]:
    vec = to_vector(embedding)
    async with pool.connection() as conn:
        cur = await conn.execute(SEARCH_SQL, (vec, vec, k))
        rows = await cur.fetchall()
    return [{"title": t, "source": s, "content": c, "score": float(sc)} for t, s, c, sc in rows]
