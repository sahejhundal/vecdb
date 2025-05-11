from shared.models.schemas import Chunk
from app.database.index.base_index import BaseIndex

import numpy as np
from typing import List, Tuple, Dict


class LSHIndex(BaseIndex):
    """
    LSH (Locality-Sensitive Hashing) index using random hyperplane projections to hash similar vectors into the same buckets.
    """
    
    def __init__(self, dimension: int, n_planes: int = 8, n_tables: int = 4, random_seed: int = 42):
        super().__init__(dimension)
        
        self.n_planes = n_planes
        self.n_tables = n_tables
        
        np.random.seed(random_seed)
        
        self.planes = []
        for _ in range(n_tables):
            random_planes = np.random.randn(n_planes, dimension)
            random_planes /= np.linalg.norm(random_planes, axis=1, keepdims=True)
            self.planes.append(random_planes)
        
        self.hash_tables: List[Dict[str, List[Chunk]]] = [
            {} for _ in range(n_tables)
        ]
    
    def _hash_vector(self, vector: np.ndarray, planes: np.ndarray) -> str:
        vector_norm = vector / (np.linalg.norm(vector) + 1e-10)
        projections = np.dot(planes, vector_norm)
        return ''.join(['1' if proj > 0 else '0' for proj in projections])
    
    def insert(self, chunk: Chunk) -> None:
        with self._lock:
            vector = np.array(chunk.embedding)
            
            for table_idx in range(self.n_tables):
                hash_key = self._hash_vector(vector, self.planes[table_idx])
                if hash_key not in self.hash_tables[table_idx]:
                    self.hash_tables[table_idx][hash_key] = []
                self.hash_tables[table_idx][hash_key].append(chunk)
    
    def search(self, query: np.ndarray, k: int = 1) -> List[Tuple[float, Chunk]]:
        with self._lock:
            candidates_dict = {}
            
            for table_idx in range(self.n_tables):
                hash_key = self._hash_vector(query, self.planes[table_idx])
                if hash_key in self.hash_tables[table_idx]:
                    for chunk in self.hash_tables[table_idx][hash_key]:
                        candidates_dict[chunk.id] = chunk
            
            if not candidates_dict:
                return []
            
            distances = []
            query_norm = query / np.linalg.norm(query)
            
            for chunk in candidates_dict.values():
                chunk_vector = np.array(chunk.embedding)
                chunk_norm = chunk_vector / np.linalg.norm(chunk_vector)
                distance = float(1 - np.dot(query_norm, chunk_norm))
                distances.append((distance, chunk))
            
            distances.sort()
            return distances[:k]
    
    def clear(self) -> None:
        with self._lock:
            self.hash_tables = [dict() for _ in range(self.n_tables)] 