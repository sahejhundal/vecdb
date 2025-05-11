from shared.models.schemas import Library
from app.database.singleton import db
from shared.models.api_schemas import LibraryCreate, LibraryUpdate
from app.database.index.lsh_index import LSHIndex
from app.database.index.vector_index import VectorIndex

from fastapi import APIRouter, HTTPException
from typing import List, Literal


router = APIRouter(prefix="/libraries", tags=["libraries"])

@router.post("", response_model=Library)
def create_library(library_create: LibraryCreate):
    return db.create_library(library_create)

@router.get("/{library_id}", response_model=Library)
def get_library(library_id: str):
    library = db.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@router.put("/{library_id}", response_model=Library)
def update_library(library_id: str, library_update: LibraryUpdate):
    library = db.update_library(
        library_update
    )
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@router.delete("/{library_id}")
def delete_library(library_id: str):
    if not db.delete_library(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    return {"status": "success"}

@router.post("/{library_id}/index")
def index_library(library_id: str):
    if not db.index_library(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    return {"status": "success"}

@router.post("/{library_id}/switch-index")
def switch_index_algorithm(library_id: str, algorithm: Literal["lsh", "vector"]):
    index_class = LSHIndex if algorithm == "lsh" else VectorIndex
    if not db.switch_index_algorithm(library_id, index_class):
        raise HTTPException(status_code=404, detail="Library not found")
    return {"status": "success", "algorithm": algorithm}

@router.get("/{library_id}/chunks/count")
def get_chunk_count(library_id: str):
    library = db.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"count": db.get_chunk_count(library_id)} 