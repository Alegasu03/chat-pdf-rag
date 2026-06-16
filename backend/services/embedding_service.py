from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    def __init__(self):
        self.model = None

    def get_model(self):
        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.model

    def embed_text(self, text: str) -> np.ndarray:
        return self.get_model().encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def embed_chunks(self, chunks: list[str]) -> np.ndarray:
        return self.get_model().encode(
            chunks,
            convert_to_numpy=True,
            normalize_embeddings=True
        )