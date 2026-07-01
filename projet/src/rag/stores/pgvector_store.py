"""
Backend Pgvector -- alternative documentee pour un SI PostgreSQL existant.
Reprend la connexion du benchmark.py original (port 5433, db ragdb)
mais enrichit le schema avec les colonnes de metadonnees.
"""
import psycopg2

from src.rag.config import cfg
from src.rag.ingestion.chunking import Chunk
from src.rag.stores.base import VectorStore

_CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS chunks (
    id          UUID PRIMARY KEY,
    text        TEXT NOT NULL,
    source      TEXT,
    page        INT,
    section     TEXT,
    chunk_index INT,
    bp_code     TEXT,
    embedding   vector({cfg.embedding.dimension})
)
"""


class PgvectorStore(VectorStore):
    def __init__(self):
        self._conn = psycopg2.connect(cfg.stores.pgvector_dsn)
        with self._conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(_CREATE_TABLE)
        self._conn.commit()

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        with self._conn.cursor() as cur:
            for chunk, vec in zip(chunks, vectors):
                cur.execute(
                    """INSERT INTO chunks
                       (id, text, source, page, section, chunk_index, bp_code, embedding)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT (id) DO NOTHING""",
                    (chunk.id, chunk.text, chunk.source, chunk.page,
                     chunk.section, chunk.chunk_index, chunk.bp_code, vec),
                )
        self._conn.commit()
        print(f"[pgvector] {len(chunks)} chunks indexes")

    def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[Chunk]:
        where, params = "", [str(vector)]
        if filters:
            conditions = " AND ".join(f"{col} = %s" for col in filters)
            where = f"WHERE {conditions}"
            params += list(filters.values())
        params.append(k)

        with self._conn.cursor() as cur:
            cur.execute(
                f"""SELECT id, text, source, page, section, chunk_index, bp_code
                    FROM chunks {where}
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s""",
                [params[0]] + params[1:],
            )
            rows = cur.fetchall()

        return [
            Chunk(
                id=str(r[0]), text=r[1], source=r[2] or "?", page=r[3] or 0,
                section=r[4] or "?", chunk_index=r[5] or 0, bp_code=r[6] or None,
            )
            for r in rows
        ]

    def count(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM chunks")
            return cur.fetchone()[0]

    def delete_collection(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS chunks")
        self._conn.commit()
        with self._conn.cursor() as cur:
            cur.execute(_CREATE_TABLE)
        self._conn.commit()
        print("[pgvector] Table chunks reinitialisee")
