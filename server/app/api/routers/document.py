from shared.models.schemas import Document, Chunk
from app.database.singleton import db
from shared.models.api_schemas import DocumentCreate, DocumentUpdate

from fastapi import APIRouter, HTTPException
from typing import List


router = APIRouter(prefix="/libraries/{library_id}/documents", tags=["documents"])

@router.post("", response_model=Document)
def create_document(document_create: DocumentCreate):
    #print("before add_document")
    result = db.add_document(document_create)
    #print("after add_document")
    if not result:
        raise HTTPException(status_code=404, detail="Library not found")
    return result

@router.get("/{document_id}", response_model=Document)
def get_document(library_id: str, document_id: str):
    document = db.get_document(library_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/{document_id}", response_model=Document)
def update_document(document_update: DocumentUpdate):
    document = db.update_document(document_update)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
def delete_document(library_id: str, document_id: str):
    if not db.delete_document(library_id, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"} 