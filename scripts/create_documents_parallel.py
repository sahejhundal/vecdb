import asyncio
import aiohttp
import uuid
from typing import List

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"  # Adjust this if your API runs on a different port

async def create_document(session: aiohttp.ClientSession, library_id: str) -> None:
    """Create a single document with empty chunks."""
    document_data = {
        "library_id": library_id,
        "document_title": f"Test Document {uuid.uuid4()}",
        "chunks": [],  # Empty chunks list
        "metadata": {}
    }
    
    url = f"{BASE_URL}/libraries/{library_id}/documents"
    async with session.post(url, json=document_data) as response:
        if response.status == 200:
            result = await response.json()
            print(f"Successfully created document: {result}")
        else:
            print(f"Failed to create document. Status: {response.status}")
            print(await response.text())

async def create_documents_parallel(library_id: str, num_documents: int = 100) -> None:
    """Create multiple documents in parallel."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            create_document(session, library_id)
            for _ in range(num_documents)
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Replace with your actual library ID
    LIBRARY_ID = "test"
    
    # Run the parallel document creation
    asyncio.run(create_documents_parallel(LIBRARY_ID)) 