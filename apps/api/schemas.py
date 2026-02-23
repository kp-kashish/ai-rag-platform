from pydantic import BaseModel
from typing import List, Optional

class DocumentCreate(BaseModel):
    filename: str
    source: Optional[str] = None

class DocumentOut(BaseModel):
    id: int
    filename: str
    source: Optional[str] = None

class ChunksCreate(BaseModel):
    chunks: List[str]
    page: Optional[int] = None  # optional for now

class ChunksOut(BaseModel):
    inserted: int
    
class ChunkOut(BaseModel):
    id: int
    document_id: int
    page: Optional[int] = None
    text: str