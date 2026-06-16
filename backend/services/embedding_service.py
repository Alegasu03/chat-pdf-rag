from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def embed_chunks(self, chunks: list[str]) -> np.ndarray:
        return self.model.encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True
        )