import sys
import json
from typing import List, Dict, Optional
import cohere
import os
from dotenv import load_dotenv
load_dotenv()

from shared.models.api_schemas import (
    LibraryCreate, LibraryUpdate,
    DocumentCreate, DocumentUpdate,
    ChunkCreate, ChunkUpdate, BulkChunkCreate,
    SearchQuery, SearchResponse
)

from vectordb_apiclient import VectorDBAPIClient

class VectorDBClient:
    def __init__(self):
        self.apiclient = VectorDBAPIClient()
        self.library_id = "default_library"
        self.co = cohere.Client(os.getenv('COHERE_API_KEY'))

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text using Cohere API."""
        try:
            response = self.co.embed(
                texts=[text],
                model='embed-english-v3.0',
                input_type='search_document'
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise

    def print_menu(self):
        """Print the main menu options."""
        print("\n=== VectorDB API Client ===")
        print("1. Library Operations")
        print("2. Document Operations")
        print("3. Chunk Operations")
        print("4. Search Operations")
        print("5. Exit")
        return input("Select an option (1-5): ")

    def print_library_menu(self):
        self.library_id = "default_library"
        print("\n=== Library Operations ===")
        print("1. Create Library")
        print("2. Get Library")
        print("3. Update Library")
        print("4. Delete Library")
        print("5. Index Library")
        print("6. Get Chunk Count")
        print("7. Switch Index Algorithm")
        print("8. Back to Main Menu")
        return input("Select an option (1-8): ")

    def print_document_menu(self):
        """Print document operation options."""
        print("\n=== Document Operations ===")
        print("1. Create Document")
        print("2. Get Document")
        print("3. Update Document")
        print("4. Delete Document")
        print("5. Back to Main Menu")
        return input("Select an option (1-5): ")

    def print_chunk_menu(self):
        """Print chunk operation options."""
        print("\n=== Chunk Operations ===")
        print("1. Create Single Chunk")
        print("2. Create Multiple Chunks")
        print("3. List Chunks")
        print("4. Get Chunk")
        print("5. Update Chunk")
        print("6. Delete Chunk")
        print("7. Back to Main Menu")
        return input("Select an option (1-7): ")

    def handle_library_operations(self):
        while True:
            self.library_id = "default_library"
            choice = self.print_library_menu()
            try:
                # Create Library
                if choice == "1":
                    self.library_id = input(f"Enter library name (default: {self.library_id}): ") or self.library_id
                    metadata_str = input("Enter metadata (JSON format, press Enter to skip): ").strip()
                    metadata = json.loads(metadata_str) if metadata_str else None
                    library = self.apiclient.create_library(LibraryCreate(library_id=self.library_id, metadata=metadata))
                    print(f"Library created successfully! ID: {library.id}")

                # Get Library
                elif choice == "2":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    library = self.apiclient.get_library(self.library_id)
                    print("\nLibrary Details:")
                    print(f"Library ID: {library.library_id}")
                    print(f"ID: {library.id}")
                    print(f"Created: {library.created_at}")
                    print(f"Updated: {library.updated_at}")
                    print(f"Is Indexed: {library.is_indexed}")
                    print(f"Metadata: {library.metadata}")
                    print(f"\nDocuments ({len(library.documents)}):")
                    
                    for doc in library.documents:
                        print(f"\nDocument: {doc.metadata.get('document_title', 'Untitled')} (ID: {doc.id})")
                        print(f"Chunks ({len(doc.chunks)}):")
                        for chunk in doc.chunks:
                            print(f"  - {chunk.text[:100]}..." if len(chunk.text) > 100 else f"  - {chunk.text}")

                # Update Library
                elif choice == "3":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    metadata_str = input("Enter new metadata (JSON format, press Enter to skip): ").strip()
                    metadata = json.loads(metadata_str) if metadata_str else None
                    library = self.apiclient.update_library(LibraryUpdate(library_id=self.library_id, metadata=metadata))
                    print("Library updated successfully!")

                # Delete Library
                elif choice == "4":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    self.apiclient.delete_library(self.library_id)
                    print("Library deleted successfully!")

                # Index Library
                elif choice == "5":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    self.apiclient.index_library(self.library_id)
                    print("Library indexed successfully!")

                # Get Chunk Count
                elif choice == "6":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    count = self.apiclient.get_chunk_count(self.library_id)
                    print(f"Chunk count: {count['count']}")

                # Switch Index Algorithm
                elif choice == "7":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    print("\nAvailable algorithms:")
                    print("1. LSH Index (faster, approximate)")
                    print("2. Vector Index (slower, exact)")
                    algo_choice = input("Select algorithm (1-2): ")
                    algorithm = "lsh" if algo_choice == "1" else "vector"
                    result = self.apiclient.switch_index_algorithm(self.library_id, algorithm)
                    print(f"Successfully switched to {algorithm} index!")

                # Back to Main Menu
                elif choice == "8":
                    break

            except Exception as e:
                print(f"Error: {str(e)}")

    def handle_document_operations(self):
        while True:
            self.library_id = "default_library"
            choice = self.print_document_menu()
            try:
                # Create Document
                if choice == "1":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_title = input("Enter document title: ")
                    metadata_str = input("Enter metadata (JSON format, press Enter to skip): ").strip()
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    metadata["document_title"] = document_title
                    
                    chunks = []
                    while True:
                        add_chunk = input("Add a chunk? (y/n): ").lower()
                        if add_chunk != 'y':
                            break
                        text = input("Enter chunk text: ")
                        embedding = self.generate_embedding(text)
                        chunks.append(ChunkCreate(
                            library_id=self.library_id,
                            text=text,
                            embedding=embedding,
                            metadata={}
                        ))
                    
                    document = self.apiclient.create_document(DocumentCreate(
                        library_id=self.library_id,
                        document_title=document_title,
                        chunks=chunks,
                        metadata=metadata
                    ))
                    print(f"Document created successfully! ID: {document.id}")

                # Get Document
                elif choice == "2":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    document = self.apiclient.get_document(self.library_id, document_id)
                    print("\nDocument Details:")
                    print(f"ID: {document.id}")
                    print(f"Title: {document.metadata.get('document_title', 'Untitled')}")
                    print(f"Created: {document.created_at}")
                    print(f"Updated: {document.updated_at}")
                    print("\nChunks:")
                    for i, chunk in enumerate(document.chunks, 1):
                        print(f"\nChunk {i}:")
                        print(f"  Text: {chunk.text}")
                        print(f"  ID: {chunk.id}")
                        print(f"  Metadata: {chunk.metadata}")

                # Update Document
                elif choice == "3":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    document_title = input("Enter new document title (press Enter to skip): ").strip()
                    metadata_str = input("Enter new metadata (JSON format, press Enter to skip): ").strip()
                    metadata = json.loads(metadata_str) if metadata_str else None
                    if document_title:
                        if metadata is None:
                            metadata = {}
                        metadata["document_title"] = document_title
                    document = DocumentUpdate(
                        library_id=self.library_id,
                        document_id=document_id,
                        document_title=document_title,
                        metadata=metadata
                    )
                    document = self.apiclient.update_document(document)
                    print("Document updated successfully!")

                # Delete Document
                elif choice == "4":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    self.apiclient.delete_document(self.library_id, document_id)
                    print("Document deleted successfully!")

                # Back to Main Menu
                elif choice == "5":
                    break

            except Exception as e:
                print(f"Error: {str(e)}")

    def handle_chunk_operations(self):
        while True:
            self.library_id = "default_library"
            choice = self.print_chunk_menu()
            try:
                # Create Single Chunk
                if choice == "1":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    text = input("Enter chunk text: ")
                    embedding = self.generate_embedding(text)
                    metadata_str = input("Enter metadata (JSON format, press Enter to skip): ").strip()
                    metadata = json.loads(metadata_str) if metadata_str else None
                    
                    chunk = self.apiclient.create_chunk(ChunkCreate(
                        library_id=self.library_id,
                        document_id=document_id,
                        text=text,
                        embedding=embedding,
                        metadata=metadata
                    ))
                    print(f"Chunk created successfully! ID: {chunk.id}")

                # Create Multiple Chunks
                elif choice == "2":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    chunks = []
                    
                    while True:
                        add_chunk = input("Add another chunk? (y/n): ").lower()
                        if add_chunk != 'y':
                            break
                        text = input("Enter chunk text: ")
                        embedding = self.generate_embedding(text)
                        chunks.append(ChunkCreate(
                            library_id=self.library_id,
                            document_id=document_id,
                            text=text,
                            embedding=embedding,
                            metadata={}
                        ))
                    
                    result = self.apiclient.create_chunks_bulk(BulkChunkCreate(chunks=chunks))
                    print(f"Created {len(result)} chunks successfully!")

                # List Chunks
                elif choice == "3":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    chunks = self.apiclient.list_chunks(self.library_id, document_id)
                    print(f"Found {len(chunks)} chunks:")
                    for chunk in chunks:
                        print(f"ID: {chunk.id}, Text: {chunk.text}, Metadata: {chunk.metadata}")

                # Get Chunk
                elif choice == "4":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    chunk_id = input("Enter chunk ID: ")
                    chunk = self.apiclient.get_chunk(self.library_id, document_id, chunk_id)
                    print(f"Chunk: {chunk}")

                # Update Chunk
                elif choice == "5":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    chunk_id = input("Enter chunk ID: ")
                    text = input("Enter new text (press Enter to skip): ").strip()
                    embedding = self.generate_embedding(text) if text else None
                    metadata_str = input("Enter new metadata (JSON format, press Enter to skip): ").strip()
                    metadata = json.loads(metadata_str) if metadata_str else None
                    
                    chunk = self.apiclient.update_chunk(self.library_id, document_id, chunk_id,
                                            text=text or None,
                                            embedding=embedding,
                                            metadata=metadata)
                    print("Chunk updated successfully!")

                # Delete Chunk
                elif choice == "6":
                    self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
                    document_id = input("Enter document ID: ")
                    chunk_id = input("Enter chunk ID: ")
                    self.apiclient.delete_chunk(self.library_id, document_id, chunk_id)
                    print("Chunk deleted successfully!")

                # Back to Main Menu
                elif choice == "7":
                    break

            except Exception as e:
                print(f"Error: {str(e)}")

    def handle_search_operations(self):
        try:
            self.library_id = "default_library"
            self.library_id = input(f"Enter library ID (default: {self.library_id}): ") or self.library_id
            query_text = input("Enter your search query text: ")
            embedding = self.generate_embedding(query_text)
            
            k = int(input("Enter number of results (default 5): ") or "5")
            metadata_str = input("Enter metadata filter (JSON format, press Enter to skip): ").strip()
            metadata_filter = json.loads(metadata_str) if metadata_str else {}

            results = self.apiclient.search(SearchQuery(
                library_id=self.library_id,
                embedding=embedding,
                k=k,
                metadata_filter=metadata_filter
            ))
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Distance: {result.distance}")
                print(f"Text: {result.chunk.text}")
                print(f"Metadata: {result.chunk.metadata}")

        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    print("Welcome to VectorDB Client!")
    client = VectorDBClient()

    while True:
        choice = client.print_menu()
        
        if choice == "1":
            client.handle_library_operations()
        elif choice == "2":
            client.handle_document_operations()
        elif choice == "3":
            client.handle_chunk_operations()
        elif choice == "4":
            client.handle_search_operations()
        elif choice == "5":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 