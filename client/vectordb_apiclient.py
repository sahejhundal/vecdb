import requests
from typing import List, Dict, Optional, Union
from shared.models.api_schemas import (
    LibraryCreate, LibraryUpdate,
    DocumentCreate, DocumentUpdate,
    ChunkCreate, ChunkUpdate, BulkChunkCreate,
    SearchQuery, SearchResponse
)
from shared.models.schemas import Library, Document, Chunk

class VectorDBAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url.rstrip('/')

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Union[Dict, List]:
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    # Library operations
    def create_library(self, library_create: LibraryCreate) -> Library:
        return Library(**self._make_request("POST", "/libraries", json=library_create.model_dump()))

    def get_library(self, library_id: str) -> Library:
        return Library(**self._make_request("GET", f"/libraries/{library_id}"))

    def update_library(self, library_update: LibraryUpdate) -> Library:
        return Library(**self._make_request("PUT", f"/libraries/{library_update.library_id}", json=library_update.dict(exclude_unset=True)))

    def delete_library(self, library_id: str) -> Dict:
        return self._make_request("DELETE", f"/libraries/{library_id}")

    def index_library(self, library_id: str) -> Dict:
        return self._make_request("POST", f"/libraries/{library_id}/index")

    def get_chunk_count(self, library_id: str) -> Dict:
        return self._make_request("GET", f"/libraries/{library_id}/chunks/count")

    def switch_index_algorithm(self, library_id: str, algorithm: str) -> Dict:
        return self._make_request("POST", f"/libraries/{library_id}/switch-index", params={"algorithm": algorithm})

    # Document operations
    def create_document(self, document_create: DocumentCreate) -> Document:
        return Document(**self._make_request("POST", f"/libraries/{document_create.library_id}/documents", json=document_create.model_dump()))

    def get_document(self, library_id: str, document_id: str) -> Document:
        return Document(**self._make_request("GET", f"/libraries/{library_id}/documents/{document_id}"))

    def update_document(self, document_update: DocumentUpdate) -> Document:
        return Document(**self._make_request("PUT", f"/libraries/{document_update.library_id}/documents/{document_update.document_id}", json=document_update.dict(exclude_unset=True)))

    def delete_document(self, library_id: str, document_id: str) -> Dict:
        return self._make_request("DELETE", f"/libraries/{library_id}/documents/{document_id}")

    # Chunk operations
    def create_chunk(self, chunk_create: ChunkCreate) -> Chunk:
        return Chunk(**self._make_request("POST", f"/libraries/{chunk_create.library_id}/documents/{chunk_create.document_id}/chunks", json=chunk_create.model_dump()))

    def create_chunks_bulk(self, bulk_chunk_create: BulkChunkCreate) -> List[Chunk]:
        response = self._make_request("POST", f"/libraries/{bulk_chunk_create.chunks[0].library_id}/documents/{bulk_chunk_create.chunks[0].document_id}/chunks/bulk", json=bulk_chunk_create.model_dump())
        return [Chunk(**chunk) for chunk in response]

    def list_chunks(self, library_id: str, document_id: str) -> List[Chunk]:
        response = self._make_request("GET", f"/libraries/{library_id}/documents/{document_id}/chunks")
        return [Chunk(**chunk) for chunk in response]

    def get_chunk(self, library_id: str, document_id: str, chunk_id: str) -> Chunk:
        return Chunk(**self._make_request("GET", f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}"))

    def update_chunk(self, chunk_update: ChunkUpdate) -> Chunk:
        return Chunk(**self._make_request("PUT", f"/libraries/{chunk_update.library_id}/documents/{chunk_update.document_id}/chunks/{chunk_update.chunk_id}", json=chunk_update.dict(exclude_unset=True)))

    def delete_chunk(self, library_id: str, document_id: str, chunk_id: str) -> Dict:
        return self._make_request("DELETE", f"/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")

    # Search operations
    def search(self, search_query: SearchQuery) -> List[SearchResponse]:
        response = self._make_request("POST", f"/libraries/{search_query.library_id}/search", json=search_query.model_dump())
        return [SearchResponse(**result) for result in response] 