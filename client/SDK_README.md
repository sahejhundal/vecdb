# VectorDB API Client SDK

This SDK provides a Python client for interacting with the VectorDB API. It offers a comprehensive set of methods for managing libraries, documents, and chunks, as well as performing vector searches.

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

```python
from client.vectordb_apiclient import VectorDBAPIClient
from shared.models.api_schemas import LibraryCreate, DocumentCreate, ChunkCreate, SearchQuery

# Initialize the client
client = VectorDBAPIClient(base_url="http://localhost:8000/api/v1")
```

## Core Features

### Library Management

Libraries are the top-level containers for your documents and chunks.

```python
# Create a new library
library = client.create_library(LibraryCreate(
    library_id="my_library",
    metadata={"description": "My first library"}
))

# Get library details
library = client.get_library("my_library")

# Update library metadata
updated_library = client.update_library(LibraryUpdate(
    library_id="my_library",
    metadata={"description": "Updated description"}
))

# Delete a library
client.delete_library("my_library")

# Index a library for search
client.index_library("my_library")

# Get chunk count in a library
count = client.get_chunk_count("my_library")

# Switch index algorithm
client.switch_index_algorithm("my_library", algorithm="lsh")  # or "vector"
```

### Document Management

Documents are collections of chunks within a library.

```python
# Create a document with chunks
document = client.create_document(DocumentCreate(
    library_id="my_library",
    document_title="My Document",
    chunks=[
        ChunkCreate(
            library_id="my_library",
            text="First chunk text",
            embedding=[0.1, 0.2, 0.3]  # Your vector embedding
        ),
        ChunkCreate(
            library_id="my_library",
            text="Second chunk text",
            embedding=[0.4, 0.5, 0.6]  # Your vector embedding
        )
    ],
    metadata={"author": "John Doe"}
))

# Get document details
document = client.get_document("my_library", "document_id")

# Update document
updated_document = client.update_document(DocumentUpdate(
    library_id="my_library",
    document_id="document_id",
    document_title="Updated Title",
    metadata={"author": "Jane Doe"}
))

# Delete a document
client.delete_document("my_library", "document_id")
```

### Chunk Management

Chunks are the smallest units of text with their associated vector embeddings.

```python
# Create a single chunk
chunk = client.create_chunk(ChunkCreate(
    library_id="my_library",
    document_id="document_id",
    text="Chunk text",
    embedding=[0.1, 0.2, 0.3],
    metadata={"section": "introduction"}
))

# Create multiple chunks in bulk
chunks = client.create_chunks_bulk(BulkChunkCreate(
    chunks=[
        ChunkCreate(
            library_id="my_library",
            document_id="document_id",
            text="First chunk",
            embedding=[0.1, 0.2, 0.3]
        ),
        ChunkCreate(
            library_id="my_library",
            document_id="document_id",
            text="Second chunk",
            embedding=[0.4, 0.5, 0.6]
        )
    ]
))

# List all chunks in a document
chunks = client.list_chunks("my_library", "document_id")

# Get a specific chunk
chunk = client.get_chunk("my_library", "document_id", "chunk_id")

# Update a chunk
updated_chunk = client.update_chunk(ChunkUpdate(
    library_id="my_library",
    document_id="document_id",
    chunk_id="chunk_id",
    text="Updated text",
    embedding=[0.7, 0.8, 0.9]
))

# Delete a chunk
client.delete_chunk("my_library", "document_id", "chunk_id")
```

### Vector Search

Perform semantic search using vector embeddings.

```python
# Search for similar chunks
results = client.search(SearchQuery(
    library_id="my_library",
    embedding=[0.1, 0.2, 0.3],  # Your query vector
    k=5,  # Number of results to return
))

# Process search results
for result in results:
    print(f"Distance: {result.distance}")
    print(f"Text: {result.chunk.text}")
    print(f"Metadata: {result.chunk.metadata}")
```

## Data Models

### Library
- `id`: Unique identifier
- `library_id`: User-defined library identifier
- `metadata`: Optional dictionary for custom metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `is_indexed`: Boolean indicating if library is indexed for search

### Document
- `id`: Unique identifier
- `document_title`: Title of the document
- `chunks`: List of associated chunks
- `metadata`: Optional dictionary for custom metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Chunk
- `id`: Unique identifier
- `text`: The text content
- `embedding`: Vector embedding of the text
- `metadata`: Optional dictionary for custom metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Error Handling

The client raises exceptions for HTTP errors:

```python
try:
    library = client.get_library("non_existent_library")
except requests.exceptions.HTTPError as e:
    print(f"Error: {e}")
```

## Best Practices

1. Always index your library after adding new documents/chunks for search functionality
2. Use bulk operations when creating multiple chunks for better performance
3. Handle API errors appropriately in your application
4. Use appropriate vector dimensions (1024) for your embeddings