from shared.models.schemas import Chunk
from app.database.index.base_index import BaseIndex

from typing import List, Tuple
import numpy as np


class VectorIndex(BaseIndex):
    def __init__(self, dimension: int):
        super().__init__(dimension)
        self.chunks: List[Chunk] = []
    
    def insert(self, chunk: Chunk) -> None:
        with self._lock:
            self.chunks.append(chunk)
    
    def search(self, query: np.ndarray, k: int = 1) -> List[Tuple[float, Chunk]]:
        with self._lock:
            if not self.chunks:
                return []
            
            query_norm = query / np.linalg.norm(query)
            
            similarities = []
            for chunk in self.chunks:
                chunk_vec = np.array(chunk.embedding)
                chunk_norm = chunk_vec / np.linalg.norm(chunk_vec)
                sim = np.dot(query_norm, chunk_norm)
                similarities.append((sim, chunk))
            
            similarities.sort(reverse=True)
            return [(1 - sim, chunk) for sim, chunk in similarities[:k]]
    
    def clear(self) -> None:
        with self._lock:
            self.chunks = []