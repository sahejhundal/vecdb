# Vector Search API Documentation

## Project Overview

This is a vector search API implementation that provides efficient storage and retrieval of document embeddings. The system uses Locality-Sensitive Hashing (LSH) for optimized similarity search and includes a Python SDK client for easy integration.

### Key Features

- RESTful API for managing document libraries, documents, and chunks
- Thread-safe vector database implementation using RLock
- Persistent storage using pickle serialization
- Automatic periodic saving of database state
- Sample embeddings initialization from a default file
- Python SDK client with interactive CLI
- Cohere integration for embedding generation

### Technical Implementation

#### Database Implementation (`db.py`)
- Thread-safe operations using `threading.RLock`
- Periodic automatic saving of database state
- Persistent storage using pickle serialization
- Automatic initialization from sample embeddings file
- Support for both LSH and brute-force vector search implementations

#### Vector Search Implementations

##### VectorIndex (`vector_index.py`)
A basic vector search implementation using brute force comparison.

###### Space Complexity
- **O(n * d)** where:
  - n = number of chunks stored
  - d = dimension of the vectors
- Storage: All vectors are stored in a list, with each vector having d dimensions

###### Time Complexity
- **Insert**: O(1)
  - Simply appends to a list
- **Search**: O(n * d)
  - Must compute similarity with every stored vector
  - Each similarity computation takes O(d) time for dot product and normalization

##### LSHIndex (`lsh_index.py`)
An optimized implementation using Locality-Sensitive Hashing (LSH).

###### Space Complexity
- **O(n * t + t * p * d)** where:
  - n = number of chunks stored
  - t = number of hash tables (n_tables)
  - p = number of planes per table (n_planes)
  - d = dimension of vectors
- Storage components:
  - Hash tables: O(n * t) - each chunk is stored t times
  - Projection planes: O(t * p * d) for the random projection matrices

###### Time Complexity
- **Insert**: O(t * (p * d + 1))
  - For each table:
    - Computing hash: O(p * d) for matrix multiplication
    - Inserting into hash table: O(1) average case
- **Search**: O(t * (p * d + b) * d)
  - Process:
    - Computing query hashes: O(t * p * d)
    - Looking up buckets: O(t)
    - Computing exact distances for candidates: O(b * d) per table
  - Where:
    - t = number of hash tables
    - p = number of planes
    - d = dimension of vectors
    - b = average bucket size

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r server/requirements.txt
   pip install -e .
   ```
4. Create a `.env` file with your Cohere API key:
   ```
   COHERE_API_KEY=your_api_key_here
   ```

## Running the Project

1. Start the server:
   ```bash
   python server/run.py
   ```
   The server will start on `http://localhost:8000`

2. Use the Python SDK client:
   ```bash
   python client/vectordb_client.py
   ```

## Containerizing

   ```bash
   eval $(minikube docker-env)
   docker build -t vectordb:1.0 .
   minikube service vectordb
   ```


## API Endpoints

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check endpoint |

### Libraries

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/libraries` | Create a new library |
| GET | `/libraries/{library_id}` | Get a library by ID |
| PUT | `/libraries/{library_id}` | Update a library |
| DELETE | `/libraries/{library_id}` | Delete a library |
| POST | `/libraries/{library_id}/index` | Index all documents in a library |
| GET | `/libraries/{library_id}/chunks/count` | Get the total number of chunks in a library |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/libraries/{library_id}/documents` | Create a new document in a library |
| GET | `/libraries/{library_id}/documents/{document_id}` | Get a document from a library |
| PUT | `/libraries/{library_id}/documents/{document_id}` | Update a document in a library |
| DELETE | `/libraries/{library_id}/documents/{document_id}` | Delete a document from a library |

### Chunks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/libraries/{library_id}/documents/{document_id}/chunks` | Create a new chunk in a document |
| POST | `/libraries/{library_id}/documents/{document_id}/chunks/bulk` | Create multiple chunks at once |
| GET | `/libraries/{library_id}/documents/{document_id}/chunks` | List all chunks in a document |
| GET | `/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}` | Get a specific chunk |
| PUT | `/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}` | Update a chunk |
| DELETE | `/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}` | Delete a chunk |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/libraries/{library_id}/search` | Search for similar chunks in a library |

## Python SDK Client

The project includes a Python SDK client (`vectordb_client.py`) that provides an interactive CLI for interacting with the vector database. The client supports:

- Library management (create, read, update, delete)
- Document management
- Chunk management (single and bulk operations)
- Vector search with metadata filtering
- Automatic embedding generation using Cohere API

## Data Persistence

The database state is automatically saved to disk using pickle serialization. The save process:
- Runs periodically (default: every 30 seconds)
- Uses atomic file operations to prevent corruption
- Maintains a backup of the previous state
- Initializes with sample embeddings if no existing data is found

## Error Handling

The system includes comprehensive error handling:
- Input validation using Pydantic models
- Thread-safe operations with RLock
- Graceful error recovery
- Detailed error messages and logging