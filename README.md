# Vector Database Implementation

This project implements a vector database with two different indexing strategies: a brute-force vector index and a Locality-Sensitive Hashing (LSH) index using random projections.

## Overview

The vector database is designed to store and efficiently retrieve high-dimensional vectors (embeddings) along with their associated metadata. It provides two different indexing strategies to balance between search accuracy and performance:

1. **Vector Index (Brute Force)**
   - Simple linear search implementation
   - Computes exact similarity scores
   - Best for small datasets or when accuracy is critical

2. **LSH Index (Random Projections)**
   - Approximate nearest neighbor search using Locality-Sensitive Hashing
   - Uses multiple hash tables with random hyperplanes
   - Optimized for larger datasets with acceptable approximation

## Technical Details

### Vector Index (Brute Force)

The `VectorIndex` class implements a straightforward approach where:
- Vectors are stored in a simple list
- Search involves computing cosine similarity with all vectors
- Results are sorted by similarity score

**Complexity Analysis:**
- Space Complexity: O(n * d) where n is number of vectors and d is dimension
- Time Complexity:
  - Insert: O(1)
  - Search: O(n * d) for computing similarities + O(n log n) for sorting

### LSH Index (Random Projections)

The `LSHIndex` class implements Locality-Sensitive Hashing using random hyperplane projections:
- Uses multiple hash tables (default: 4)
- Each table has multiple random hyperplanes (default: 8)
- Vectors are hashed into buckets based on their projections
- Search only considers vectors in the same buckets

**Complexity Analysis:**
- Space Complexity: O(n * d + t * p * d) where:
  - n is number of vectors
  - d is dimension
  - t is number of hash tables
  - p is number of hyperplanes per table
- Time Complexity:
  - Insert: O(t * p * d) for computing hashes
  - Search: O(t * p * d + m * d) where m is number of candidates in matching buckets


## Configuration

The LSH Index can be configured with the following parameters:
- `dimension`: Dimension of the vectors
- `n_planes`: Number of random hyperplanes per hash table (default: 8)
- `n_tables`: Number of hash tables (default: 4)
- `random_seed`: Seed for random number generation (default: 42)

## Thread Safety

Both index implementations are thread-safe, using locks to protect concurrent access to the data structures. 

## API Endpoints

The vector database exposes a RESTful API with the following endpoints:

### Libraries

- `POST /libraries` - Create a new library
- `GET /libraries/{library_id}` - Get library details
- `PUT /libraries/{library_id}` - Update library
- `DELETE /libraries/{library_id}` - Delete library
- `POST /libraries/{library_id}/index` - Index all documents in a library
- `GET /libraries/{library_id}/chunks/count` - Get total chunk count in a library

### Documents

- `POST /libraries/{library_id}/documents` - Create a new document
- `GET /libraries/{library_id}/documents/{document_id}` - Get document details
- `PUT /libraries/{library_id}/documents/{document_id}` - Update document
- `DELETE /libraries/{library_id}/documents/{document_id}` - Delete document

### Chunks

- `POST /libraries/{library_id}/documents/{document_id}/chunks` - Create a new chunk
- `POST /libraries/{library_id}/documents/{document_id}/chunks/bulk` - Create multiple chunks
- `GET /libraries/{library_id}/documents/{document_id}/chunks` - List all chunks in a document
- `GET /libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}` - Get chunk details
- `PUT /libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}` - Update chunk
- `DELETE /libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}` - Delete chunk

### Search

- `POST /libraries/{library_id}/search` - Search for similar chunks in a library
  - Request body should include:
    - `embedding`: Vector to search for
    - `k`: Number of results to return (default: 1)

### Health Check

- `GET /health` - Check API health status

## Request/Response Models

### Library
```python
class LibraryCreate:
    name: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]

class LibraryUpdate:
    name: Optional[str]
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

### Document
```python
class DocumentCreate:
    title: str
    content: str
    metadata: Optional[Dict[str, Any]]

class DocumentUpdate:
    title: Optional[str]
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

### Chunk
```python
class ChunkCreate:
    text: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]]

class ChunkUpdate:
    text: Optional[str]
    embedding: Optional[List[float]]
    metadata: Optional[Dict[str, Any]]

class BulkChunkCreate:
    chunks: List[ChunkCreate]
```

### Search
```python
class SearchQuery:
    embedding: List[float]
    k: int = 1
    metadata_filter: Optional[Dict[str, Any]]

class SearchResponse:
    distance: float
    chunk: Chunk
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request (e.g., invalid embedding dimension)
- 404: Not Found (e.g., library/document/chunk not found)
- 500: Internal Server Error

All error responses include a detail message explaining the error. 

## Project Setup and Running

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the project in development mode:
```bash
pip install -r server/requirements.txt
pip install -e .
```

This will install the project and its dependencies, and create the necessary egg-info directory.

### Running the Server

1. Start the FastAPI server:
```bash
python server/run.py
```

The server will start on `http://localhost:8000` by default. 

### Using the Client

The project includes a Python client (`client/vectordb_client.py`) that provides a convenient interface to interact with the vector database. For detailed documentation on how to use the SDK programmatically, including all available methods and examples, please refer to the [SDK Documentation](client/SDK_README.md).

The SDK provides comprehensive functionality for:
- Library management (create, read, update, delete)
- Document management with bulk operations
- Chunk management
- Chunk searching using text
- Error handling and best practices

## Containerization and Deployment

### Building the Docker Image

1. Build the Docker image:
```bash
docker build -t vectordb:latest .
```

### Kubernetes Deployment with Minikube

1. Start Minikube:
```bash
minikube start
```

2. Enable the Minikube Docker daemon:
```bash
eval $(minikube docker-env)
```

3. Build the image in Minikube's Docker environment:
```bash
docker build -t vectordb:latest .
```

4. Deploy to Kubernetes:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

5. Open the service in your browser:
```bash
minikube service vectordb-service
```

This will automatically open your default browser to the service URL.

### Accessing the Service

After deployment, you can access the service in several ways:

1. Through Minikube service (opens in browser):
```bash
minikube service vectordb-service
```

2. Get the service URL:
```bash
minikube service vectordb-service --url
```

3. Port forward to localhost:
```bash
kubectl port-forward service/vectordb-service 8000:8000
```

### Monitoring and Logs

View the deployment status:
```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

View container logs:
```bash
kubectl logs -f deployment/vectordb
```

### Cleanup

To clean up the deployment:
```bash
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
minikube stop
```