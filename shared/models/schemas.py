from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import numpy as np
import random
import string
import time

class LoggedModel(BaseModel):
    id: str = Field(default_factory=lambda: f"{int(time.time() * 1000)}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=4))}")
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Chunk(LoggedModel):
    text: str
    embedding: List[float]

    def to_vector(self) -> np.ndarray:
        return np.array(self.embedding)

class Document(LoggedModel):
    document_title: str
    chunks: List[Chunk] = Field(default_factory=list)

class Library(LoggedModel):
    library_id: str
    documents: List[Document] = Field(default_factory=list)
    is_indexed: bool = Field(default=False) 