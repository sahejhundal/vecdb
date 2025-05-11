from shared.models.schemas import Chunk

from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
import threading

class BaseIndex(ABC):
    """Abstract base class for vector indices."""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self._lock = threading.RLock()
    
    @abstractmethod
    def insert(self, chunk: Chunk) -> None:
        """Insert a chunk into the index."""

        pass
    
    @abstractmethod
    def search(self, query: np.ndarray, k: int = 1) -> List[Tuple[float, Chunk]]:
        """Search for k nearest neighbors."""

        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the index."""

        pass 