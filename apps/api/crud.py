from sqlalchemy.orm import Session
from sqlalchemy import select, text
from models import Document, Chunk
from embeddings import embed_text
import json

def create_document(db: Session, filename: str, source: str | None = None) -> Document:
    doc = Document(filename=filename, source=source)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(db: Session) -> list[Document]:
    return list(db.scalars(select(Document)).all())

def add_chunks(db: Session, document_id: int, chunks: list[str], page: int | None = None) -> int:
    objs = []
    for txt in chunks:
        vector = embed_text(txt)
        objs.append(
            Chunk(
                document_id=document_id,
                text=txt,
                page=page,
                embedding=vector
            )
        )

    db.add_all(objs)
    db.commit()
    return len(objs)

def get_chunks_for_document(db: Session, document_id: int) -> list[Chunk]:
    return list(db.scalars(select(Chunk).where(Chunk.document_id == document_id)).all())

def semantic_search(db: Session, query: str, top_k: int = 3):
    query_vector = embed_text(query)

    # Convert list to string representation for Postgres vector
    query_vector_str = json.dumps(query_vector)

    sql = text("""
        SELECT id, document_id, page, text,
               1 - (embedding <=> CAST(:query_vector AS vector)) AS score
        FROM chunks
        ORDER BY embedding <=> CAST(:query_vector AS vector)
        LIMIT :top_k;
    """)

    results = db.execute(sql, {
        "query_vector": query_vector_str,
        "top_k": top_k
    })

    return results.fetchall()