from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from pgvector.sqlalchemy import Vector
from sqlalchemy import text
import numpy as np
from src.core.config import settings
from src.models.pages_index import PagesIndex
from src.schemas.search_engine import PageRegisterInput, SearchQuery, SearchResult

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def _embed_text(text: str) -> list[float]:
    """
    Wraps OpenAI embed call using OpenAI SDK v1.0+ syntax.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]  # must be a list
    )
    return response.data[0].embedding


def register_page(
    db: Session,
    payload: PageRegisterInput,
) -> str:
    """
    1. Embed the payload.text
    2. Upsert the PagesIndex row
    Returns the page id.
    """
    vector = _embed_text(payload.text)

    page = PagesIndex(
        id=payload.id,
        author=payload.author,
        local_url=payload.local_url,
        embedding_vector=vector
    )
    db.merge(page)    
    db.commit()

    return payload.id

def search_pages(
    db: Session,
    payload: SearchQuery,
) -> list[SearchResult]:
    """
    Embed the query and perform a pgvector nearest-neighbor search
    by inlining a vector literal into the SQL.
    """
    query_vec = np.array(_embed_text(payload.query))
    vec_literal = "[{}]".format(",".join(map(str, query_vec.tolist())))

    sql = text(f"""
        SELECT
          id,
          author,
          local_url,
          embedding_vector <=> '{vec_literal}'::vector AS distance
        FROM pages_index
        ORDER BY distance
        LIMIT :limit;
    """)

    rows = db.execute(sql, {"limit": payload.top_k}).fetchall()

    return [
        SearchResult(
            id=row.id,
            author=row.author,
            local_url=row.local_url,
            distance=row.distance,
        )
        for row in rows
    ]

def delete_page(db: Session, page_id: str) -> PagesIndex | None:
    """
    Deletes a page from the PagesIndex table by its ID.
    Returns the deleted PagesIndex object if found and deleted, else None.
    """
    page = db.query(PagesIndex).filter(PagesIndex.id == page_id).first()
    if page:
        db.delete(page)
        db.commit()
        return page
    return None





