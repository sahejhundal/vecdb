from shared.models.schemas import Library, Document, Chunk
from app.database.index.base_index import BaseIndex
from app.database.index.lsh_index import LSHIndex
from app.database.index.vector_index import VectorIndex
from shared.models.api_schemas import (
    LibraryCreate,
    LibraryUpdate,
    DocumentCreate,
    ChunkCreate,
    DocumentUpdate,
    ChunkUpdate,
    SearchQuery,
)

import threading
import numpy as np
from datetime import datetime
import json
import os
from typing import List, Dict, Optional, Tuple, Type
import pickle
from pathlib import Path
import time

class VectorDatabase:
    """
    Thread-safe vector database implementation.
    
    This class provides thread-safe operations for managing document libraries and their vector indices.
    All operations are protected by a Rlock to prevent data races between concurrent reads and writes.
    The locking strategy uses a database-level lock which ensures complete consistency but may impact concurrent performance with many simultaneous operations.
    """
    



    ### INITIALIZATION ###

    def __init__(self, embedding_dimension: int = 1024, index_class: Type[BaseIndex] = LSHIndex, 
                 data_dir: str = "pickle_db", save_interval: int = 30, check_save_interval: int = 5, **index_kwargs):
        self._libraries: Dict[str, Library] = {}
        self._indices: Dict[str, BaseIndex] = {}
        self._lock = threading.RLock()
        self.embedding_dimension = embedding_dimension
        self._index_class = index_class
        self._index_kwargs = index_kwargs
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Periodic save settings
        self.save_interval = save_interval 
        self.check_save_interval = check_save_interval
        self._last_save = datetime.now()
        self._needs_save = False
        self._start_periodic_save()
        
        # Try to load from disk first
        self._load_from_disk()
        
        # If no data on disk, initialize with embeddings file
        if not self._libraries:
            self._initialize_from_embeddings_file()

    def _start_periodic_save(self):
        """Start the periodic save thread."""
        def save_worker():
            while True:
                time.sleep(self.check_save_interval)
                with self._lock:
                    now = datetime.now()
                    if self._needs_save and (now - self._last_save).total_seconds() >= self.save_interval:
                        self.save_to_disk()
                        self._last_save = now
                        self._needs_save = False
                        print(f"Saved database to disk at {now}")
        save_thread = threading.Thread(target=save_worker, daemon=True)
        save_thread.start()

    def _mark_for_save(self):
        """Mark the database as needing to be saved."""
        with self._lock:
            self._needs_save = True

    def _initialize_from_embeddings_file(self):
        """Initialize the database with embeddings from a file if it exists."""

        print(f"Initializing database from embeddings file")
        embeddings_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sample_embeddings', 'embeddings.txt')
        if not os.path.exists(embeddings_path):
            return

        with open(embeddings_path, 'r') as f:
            embeddings_data = json.load(f)
        
        library = self.create_library(LibraryCreate(library_id="default_library"))
        
        chunks_by_doc = {}
        for item in embeddings_data:
            doc_title = item.get('metadata', {}).get('document_title', 'Untitled')
            if doc_title not in chunks_by_doc:
                chunks_by_doc[doc_title] = []
            chunks_by_doc[doc_title].append(item)
        
        # First create all documents
        documents = {}
        for doc_title, chunks in chunks_by_doc.items():
            doc_metadata = {"document_title": doc_title}
            document_create = DocumentCreate(
                library_id=library.library_id,
                document_title=doc_title,
                chunks=[],
                metadata=doc_metadata
            )
            document = self.add_document(document_create)
            if document:
                documents[doc_title] = document
        
        for doc_title, chunks in chunks_by_doc.items():
            document = documents.get(doc_title)
            if document:
                for item in chunks:
                    chunk_create = ChunkCreate(
                        library_id=library.library_id,
                        document_id=document.id,  # Use the generated document ID
                        text=item['text'],
                        embedding=item['embedding'],
                        metadata=item.get('metadata', {}) or {}
                    )
                    self.add_chunk(chunk_create)
        
        self.index_library(library.library_id)
        print(f"Initialized database with {len(embeddings_data)} embeddings in {len(documents)} documents")
        
        # Save to disk after initialization
        self.save_to_disk()
        print("Saved initialized database to disk")

    def save_to_disk(self) -> bool:
        """Save the current database state to disk."""
        print(f"Saving database to disk")
        try:
            with self._lock:
                db_state = {
                    'libraries': self._libraries,
                    'embedding_dimension': self.embedding_dimension,
                    'index_class': self._index_class,
                    'index_kwargs': self._index_kwargs
                }
                
                temp_path = self._get_db_path().with_suffix('.tmp')
                with open(temp_path, 'wb') as f:
                    pickle.dump(db_state, f)
                
                temp_path.rename(self._get_db_path())
                self._last_save = datetime.now()
                self._needs_save = False
                return True
        except Exception as e:
            print(f"Error saving database state: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False

    def _load_from_disk(self) -> bool:
        """Load the database state from disk."""

        print(f"Loading database from disk")
        db_path = self._get_db_path()
        if not db_path.exists():
            return False
            
        try:
            with open(db_path, 'rb') as f:
                db_state = pickle.load(f)
                
            self._libraries = db_state['libraries']
            self.embedding_dimension = db_state['embedding_dimension']
            self._index_class = db_state['index_class']
            self._index_kwargs = db_state['index_kwargs']
            
            # Reinitialize indices
            self._indices = {
                lib_id: self._index_class(dimension=self.embedding_dimension, **self._index_kwargs)
                for lib_id in self._libraries
            }
            
            # Reindex all libraries
            for lib_id in self._libraries:
                self.index_library(lib_id)

            print(f"Loaded database from disk")
            print(f"Initialized database with {len(self._libraries)} libraries")
                
            return True
        except Exception as e:
            print(f"Error loading database state: {e}")
            return False

    def _get_db_path(self) -> Path:
        """Get the path to the database file."""
        return self.data_dir / "vector_db.pkl"




    ### LIBRARY MANAGEMENT ###
        
    def create_library(self, library_create: LibraryCreate) -> Library:
        with self._lock:
            library = Library(
                library_id=library_create.library_id,
                metadata=library_create.metadata or {}
            )
            self._libraries[library.library_id] = library
            self._indices[library.library_id] = self._index_class(dimension=self.embedding_dimension, **self._index_kwargs)

            print(f"Created library {library.library_id}")
            self._mark_for_save()
            return library
    
    def get_library(self, library_id: str) -> Optional[Library]:
        with self._lock:
            return self._libraries.get(library_id)
    
    def update_library(self, library_update: LibraryUpdate) -> Optional[Library]:
        with self._lock:
            library = self._libraries.get(library_update.library_id)
            if library:
                if library_update.metadata is not None:
                    library.metadata.update(library_update.metadata)
                library.updated_at = datetime.now()
                print(f"Updated library {library.library_id}")
                self._mark_for_save()
            else:
                print(f"update_library: Library {library_update.library_id} not found")
            return library
    
    def delete_library(self, library_id: str) -> bool:
        with self._lock:
            if library_id in self._libraries:
                del self._libraries[library_id]
                del self._indices[library_id]
                print(f"Deleted library {library_id}")
                self._mark_for_save()
                return True
            print(f"delete_library: Library {library_id} not found")
            return False
    
    def index_library(self, library_id: str) -> bool:
        with self._lock:
            library = self._libraries.get(library_id)
            if not library:
                print(f"index_library: Library {library_id} not found")
                return False
                
            index = self._indices[library_id]
            index.clear()
            
            for doc in library.documents:
                for chunk in doc.chunks:
                    index.insert(chunk)
                    
            library.is_indexed = True
            library.updated_at = datetime.now()
            print(f"Indexed library {library_id}")
            self._mark_for_save()
            return True
    
    def search(self, library_search: SearchQuery) -> List[Tuple[float, Chunk]]:
        with self._lock:
            library = self._libraries.get(library_search.library_id)
            if not library or not library.is_indexed:
                print(f"search: Library {library_search.library_id} not found or not indexed")
                return []
                
            index = self._indices[library_search.library_id]
            results = index.search(np.array(library_search.embedding), library_search.k)
            
            if library_search.metadata_filter:
                filtered_results = []
                for dist, chunk in results:
                    if all(chunk.metadata.get(k) == v for k, v in library_search.metadata_filter.items()):
                        filtered_results.append((dist, chunk))
                return filtered_results
                
            return results




    ### DOCUMENT MANAGEMENT ###

    def add_document(self, document_create: DocumentCreate) -> Optional[Document]:
        with self._lock:
            library = self._libraries.get(document_create.library_id)
            if library:
                if hasattr(document_create, "document_title") and document_create.document_title:
                    document_create.metadata["document_title"] = document_create.document_title
                elif "document_title" in document_create.metadata:
                    document_create.document_title = document_create.metadata["document_title"]
                else:
                    document_create.document_title = "Untitled"
                    document_create.metadata["document_title"] = "Untitled"

                # Create document first without chunks
                document = Document(
                    document_title=document_create.document_title,
                    chunks=[],
                    metadata=document_create.metadata
                )

                library.documents.append(document)
                library.updated_at = datetime.now()
                print(f"add_document: Document \"{document_create.document_title}\" added to library {document_create.library_id}")

                # Now add chunks with proper document ID
                for chunk in document_create.chunks:
                    chunk_create = ChunkCreate(
                        library_id=document_create.library_id,
                        document_id=document.id,
                        text=chunk.text,
                        embedding=chunk.embedding,
                        metadata=chunk.metadata or {}
                    )
                    self.add_chunk(chunk_create)

                self._mark_for_save()
                return document
            print(f"add_document: Library {document_create.library_id} not found")
            return None
    
    def get_document(self, library_id: str, document_id: str) -> Optional[Document]:
        with self._lock:
            library = self._libraries.get(library_id)
            if library:
                for doc in library.documents:
                    if doc.id == document_id:
                        print(f"get_document: Document {document_id} found in library {library_id}")
                        return doc
            print(f"get_document: Document {document_id} not found in library {library_id}")
            return None
    
    def update_document(self, document_update: DocumentUpdate) -> Optional[Document]:
        with self._lock:
            library = self._libraries.get(document_update.library_id)
            if library:
                for doc in library.documents:
                    if doc.id == document_update.document_id:
                        if document_update.document_title is not None:
                            doc.document_title = document_update.document_title
                        if document_update.chunks is not None:
                            doc.chunks = document_update.chunks
                        if document_update.metadata is not None:
                            doc.metadata.update(document_update.metadata)
                            if "document_title" in document_update.metadata:
                                doc.document_title = document_update.metadata["document_title"]
                        doc.updated_at = datetime.now()
                        print(f"update_document: Document {document_update.document_id} updated in library {document_update.library_id}")
                        self._mark_for_save()
                        return doc
            print(f"update_document: Document {document_update.document_id} not found in library {document_update.library_id}")
            return None
    
    def delete_document(self, library_id: str, document_id: str) -> bool:
        with self._lock:
            library = self._libraries.get(library_id)
            if library:
                for i, doc in enumerate(library.documents):
                    if doc.id == document_id:
                        library.documents.pop(i)
                        library.updated_at = datetime.now()
                        print(f"delete_document: Document {document_id} deleted from library {library_id}")
                        self._mark_for_save()
                        return True
            print(f"delete_document: Document {document_id} not found in library {library_id}")
            return False
    
    


    ### CHUNK MANAGEMENT ###

    def add_chunk(self, chunk_create: ChunkCreate) -> Optional[Chunk]:
        with self._lock:
            document = self.get_document(chunk_create.library_id, chunk_create.document_id)
            if document:
                chunk_metadata = {
                    "document_id": document.id,
                    "document_title": document.document_title,
                    **(chunk_create.metadata or {})
                }
                
                chunk = Chunk(
                    text=chunk_create.text,
                    embedding=chunk_create.embedding,
                    metadata=chunk_metadata
                )
                document.chunks.append(chunk)
                document.updated_at = datetime.now()
                
                if "document_title" in chunk.metadata and "document_title" not in document.metadata:
                    document.metadata["document_title"] = chunk.metadata["document_title"]
                
                library = self._libraries.get(chunk_create.library_id)
                if library and library.is_indexed:
                    self._indices[chunk_create.library_id].insert(chunk)
                    print(f"add_chunk: Chunk {chunk.id} added to library {chunk_create.library_id}")
                    self._mark_for_save()
                return chunk
            print(f"add_chunk: Library {chunk_create.library_id} not found")
            return None

    def get_chunk(self, library_id: str, document_id: str, chunk_id: str) -> Optional[Chunk]:
        with self._lock:
            document = self.get_document(library_id, document_id)
            if document:
                for chunk in document.chunks:
                    if chunk.id == chunk_id:
                        print(f"get_chunk: Chunk {chunk.id} found in library {library_id}")
                        return chunk
            print(f"get_chunk: Chunk {chunk_id} not found in library {library_id}")
            return None

    def update_chunk(self, chunk_update: ChunkUpdate) -> Optional[Chunk]:
        with self._lock:
            document = self.get_document(chunk_update.library_id, chunk_update.document_id)
            if document:
                for chunk in document.chunks:
                    if chunk.id == chunk_update.chunk_id:
                        if chunk_update.text is not None:
                            chunk.text = chunk_update.text
                        if chunk_update.embedding is not None:
                            chunk.embedding = chunk_update.embedding
                        if chunk_update.metadata is not None:
                            chunk.metadata.update(chunk_update.metadata)
                        chunk.updated_at = datetime.now()
                        self._mark_for_save()
                        print(f"update_chunk: Chunk {chunk_update.chunk_id} updated in library {chunk_update.library_id}")
                        
                        library = self._libraries.get(chunk_update.library_id)
                        if library and library.is_indexed:
                            self.index_library(chunk_update.library_id)
                        
                        return chunk
            print(f"update_chunk: Chunk {chunk_update.chunk_id} not found in library {chunk_update.library_id}")
            return None

    def delete_chunk(self, library_id: str, document_id: str, chunk_id: str) -> bool:
        with self._lock:
            document = self.get_document(library_id, document_id)
            if document:
                for i, chunk in enumerate(document.chunks):
                    if chunk.id == chunk_id:
                        document.chunks.pop(i)
                        document.updated_at = datetime.now()
                        
                        library = self._libraries.get(library_id)
                        if library and library.is_indexed:
                            self.index_library(library_id)
                        
                        self._mark_for_save()
                        return True
            print(f"delete_chunk: Chunk {chunk_id} not found in library {library_id}")
            return False

    def get_chunk_count(self, library_id: str) -> int:
        with self._lock:
            library = self._libraries.get(library_id)
            if not library:
                print(f"get_chunk_count: Library {library_id} not found")
                return 0
            print(f"get_chunk_count: Library {library_id} has {sum(len(doc.chunks) for doc in library.documents)} chunks")
            return sum(len(doc.chunks) for doc in library.documents) 