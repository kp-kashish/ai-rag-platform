from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session

from db import ping_db, check_pgvector, create_tables, get_db
from schemas import DocumentCreate, DocumentOut, ChunksCreate, ChunksOut, ChunkOut
import crud

import pdfplumber
from utils import simple_chunk_text
from schemas import SearchRequest, SearchResult

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
    
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1) Save document meta
    filename = file.filename
    doc = crud.create_document(db, filename=filename, source="upload")

    # 2) Read PDF text
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # 3) Chunk the text
    chunks = simple_chunk_text(text)

    # 4) Insert chunks
    crud.add_chunks(db, document_id=doc.id, chunks=chunks)

    return {
        "document_id": doc.id,
        "filename": filename,
        "chunks_created": len(chunks)
    }
    
@app.post("/search", response_model=list[SearchResult])
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    results = crud.semantic_search(db, payload.query, payload.top_k)

    return [
        {
            "id": r.id,
            "document_id": r.document_id,
            "page": r.page,
            "text": r.text,
            "score": float(r.score)
        }
        for r in results
    ]