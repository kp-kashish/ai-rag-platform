from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from db import ping_db, check_pgvector, create_tables, get_db
from schemas import DocumentCreate, DocumentOut, ChunksCreate, ChunksOut, ChunkOut
import crud

app = FastAPI(title="AI RAG Platform API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db/ping")
def db_ping():
    try:
        ping_db()
        return {"db": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/pgvector")
def db_pgvector():
    try:
        check_pgvector()
        return {"pgvector": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/init")
def db_init():
    try:
        create_tables()
        return {"tables": "created_or_already_exist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a document
@app.post("/documents", response_model=DocumentOut)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    doc = crud.create_document(db, filename=payload.filename, source=payload.source)
    return {"id": doc.id, "filename": doc.filename, "source": doc.source}

# List documents
@app.get("/documents", response_model=list[DocumentOut])
def get_documents(db: Session = Depends(get_db)):
    docs = crud.list_documents(db)
    return [{"id": d.id, "filename": d.filename, "source": d.source} for d in docs]

# Add chunks to a document
@app.post("/documents/{document_id}/chunks", response_model=ChunksOut)
def add_chunks(document_id: int, payload: ChunksCreate, db: Session = Depends(get_db)):
    inserted = crud.add_chunks(db, document_id=document_id, chunks=payload.chunks, page=payload.page)
    return {"inserted": inserted}

@app.get("/documents/{document_id}/chunks", response_model=list[ChunkOut])
def get_chunks(document_id: int, db: Session = Depends(get_db)):
    chunks = crud.get_chunks_for_document(db, document_id=document_id)
    return [
        {"id": c.id, "document_id": c.document_id, "page": c.page, "text": c.text}
        for c in chunks
    ]