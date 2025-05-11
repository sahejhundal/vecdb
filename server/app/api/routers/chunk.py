from shared.models.schemas import Chunk
from app.database.singleton import db
from shared.models.api_schemas import (
    ChunkCreate, ChunkUpdate, BulkChunkCreate,
    SearchQuery, SearchResponse
)

from fastapi import APIRouter, HTTPException
from typing import List
import numpy as np
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/libraries/{library_id}/documents/{document_id}/chunks", tags=["chunks"])

@router.post("", response_model=Chunk)
def create_chunk(library_id: str, document_id: str, chunk: ChunkCreate):
    """Create a new chunk in a document."""
    document = db.get_document(library_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = db.add_chunk(chunk)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result

@router.post("/bulk", response_model=List[Chunk])
def create_chunks_bulk(library_id: str, document_id: str, bulk_chunks: BulkChunkCreate):
    """Create multiple chunks in a document."""
    document = db.get_document(library_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    results = []
    for chunk_create in bulk_chunks.chunks:
        result = db.add_chunk(chunk_create)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        results.append(result)
    return results

@router.get("", response_model=List[Chunk])
def list_chunks(library_id: str, document_id: str):
    """List all chunks in a document."""
    document = db.get_document(library_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.chunks

@router.get("/{chunk_id}", response_model=Chunk)
def get_chunk(library_id: str, document_id: str, chunk_id: str):
    """Get a chunk from a document."""
    chunk = db.get_chunk(library_id, document_id, chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk

@router.put("/{chunk_id}", response_model=Chunk)
def update_chunk(library_id: str, document_id: str, chunk_id: str, chunk_update: ChunkUpdate):
    """Update a chunk in a document."""
    chunk = db.update_chunk(
        library_id,
        document_id,
        chunk_id,
        text=chunk_update.text,
        embedding=chunk_update.embedding,
        metadata=chunk_update.metadata
    )
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk

@router.delete("/{chunk_id}")
def delete_chunk(library_id: str, document_id: str, chunk_id: str):
    """Delete a chunk from a document."""
    if not db.delete_chunk(library_id, document_id, chunk_id):
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"status": "success"}

# Create a separate router for search functionality
search_router = APIRouter(prefix="/libraries/{library_id}", tags=["search"])

@search_router.post("/search", response_model=List[SearchResponse])
def search(library_id: str, query: SearchQuery):
    """Search for similar chunks in a library."""

    try:
        if len(query.embedding) != db.embedding_dimension:
            raise HTTPException(
                status_code=400,
                detail=f"Embedding dimension mismatch. Expected {db.embedding_dimension}, got {len(query.embedding)}"
            )
        
        query_embedding = np.array(query.embedding)
        if not np.all(np.isfinite(query_embedding)):
            raise HTTPException(
                status_code=400,
                detail="Invalid embedding values: contains NaN or Inf"
            )
            
        print(f"Searching for {query.k} chunks in library {library_id} with metadata filter {query.metadata_filter}")
        results = db.search(query)
        print(f"Found {len(results)} results")
        
        if results is None:
            raise HTTPException(status_code=404, detail="Library not found")
            
        return [
            SearchResponse(
                distance=float(dist),
                chunk=chunk
            ) for dist, chunk in results
        ]
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}", exc_info=True) 