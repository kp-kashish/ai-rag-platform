from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Document, Chunk


def create_document(db: Session, filename: str, source: str | None = None) -> Document:
    doc = Document(filename=filename, source=source)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def list_documents(db: Session) -> list[Document]:
    return list(db.scalars(select(Document)).all())

def add_chunks(db: Session, document_id: int, chunks: list[str], page: int | None = None) -> int:
    objs = [Chunk(document_id=document_id, text=txt, page=page) for txt in chunks]
    db.add_all(objs)
    db.commit()
    return len(objs)

def get_chunks_for_document(db: Session, document_id: int) -> list[Chunk]:
    return list(db.scalars(select(Chunk).where(Chunk.document_id == document_id)).all())