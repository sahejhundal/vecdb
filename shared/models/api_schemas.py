from typing import List, Dict, Optional
from pydantic import BaseModel
from .schemas import Chunk



"""Library"""
class LibraryCreate(BaseModel):
    library_id: str
    metadata: Optional[Dict] = {}

class LibraryUpdate(BaseModel):
    library_id: str
    metadata: Optional[Dict] = {}



"""Chunk"""
class ChunkCreate(BaseModel):
    library_id: str
    document_id: Optional[str] = None
    text: str
    embedding: List[float]
    metadata: Optional[Dict] = {}

class ChunkUpdate(BaseModel):
    library_id: str
    document_id: str
    chunk_id: str
    text: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict] = {}

class BulkChunkCreate(BaseModel):
    chunks: List[ChunkCreate]    



"""Document"""
class DocumentCreate(BaseModel):
    library_id: str
    document_title: str
    chunks: List[ChunkCreate]
    metadata: Optional[Dict] = {}

class DocumentUpdate(BaseModel):
    library_id: str
    document_id: str
    document_title: Optional[str] = None
    chunks: Optional[List[ChunkCreate]] = None
    metadata: Optional[Dict] = {}



"""Search"""

class SearchQuery(BaseModel):
    library_id: str
    embedding: List[float]
    k: int = 1
    metadata_filter: Optional[Dict] = {}

class SearchResponse(BaseModel):
    distance: float
    chunk: Chunk

    class Config:
        json_encoders = {
            float: lambda v: float(v)  # Ensure floats are properly serialized
        }
        arbitrary_types_allowed = True  # Allow Chunk type