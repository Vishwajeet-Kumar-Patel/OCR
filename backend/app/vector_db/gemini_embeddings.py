from typing import List

import httpx
from langchain_core.embeddings import Embeddings


class GeminiRESTEmbeddings(Embeddings):
    def __init__(self, api_key: str, model: str = "models/embedding-001") -> None:
        self.api_key = api_key
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(text, task_type="RETRIEVAL_DOCUMENT") for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text, task_type="RETRIEVAL_QUERY")

    def _embed_text(self, text: str, task_type: str) -> List[float]:
        model_path = self.model if self.model.startswith("models/") else f"models/{self.model}"
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:embedContent?key={self.api_key}"
        payload = {
            "content": {"parts": [{"text": text}]},
            "taskType": task_type
        }

        with httpx.Client(timeout=60) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        return data.get("embedding", {}).get("values", [])
