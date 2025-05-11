from shared.models.schemas import Library
from app.database.singleton import db
from shared.models.api_schemas import LibraryCreate, LibraryUpdate

from fastapi import APIRouter, HTTPException
from typing import List


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

@router.get("/{library_id}/chunks/count")
def get_chunk_count(library_id: str):
    library = db.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"count": db.get_chunk_count(library_id)} 