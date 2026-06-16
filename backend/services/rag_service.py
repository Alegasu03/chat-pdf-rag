import numpy as np


class RAGService:
    def __init__(self, pdf_store, embedding_service):
        self.pdf_store = pdf_store
        self.embedding_service = embedding_service

    def select_best_doc(self, query_embedding):
        best_doc_id = None
        best_score = -1

        for doc_id, doc in self.pdf_store.items():
            doc_embedding = doc["doc_embedding"]

            score = float(np.dot(query_embedding, doc_embedding))

            if score > best_score:
                best_score = score
                best_doc_id = doc_id

        return best_doc_id

    def retrieve_chunks(self, doc_id, query_embedding, top_k=3):
        if doc_id not in self.pdf_store:
            return []

        doc = self.pdf_store[doc_id]

        chunks = doc["chunks"]
        embeddings = doc["embeddings"]

        if len(chunks) == 0:
            return []

        scores = np.dot(embeddings, query_embedding)

        top_k = min(top_k, len(chunks))
        top_indices = np.argsort(scores)[-top_k:][::-1]

        return [chunks[i] for i in top_indices]